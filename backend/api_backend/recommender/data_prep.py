import os
import argparse
import pandas as pd
import numpy as np
from io import BytesIO
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import logging
import mlflow

def score_interactions(interactions_df):
    """
    This method assigns scores to each user-item interaction.
    Negative scores are prioritized when both positive and negative interactions exist.
    """
    score_map = {
            'Viewed': 2,
            'Like': 3,
            'Dislike': -3,
            'Report': -4,
            'Share': 5,
            'Comment': 4
        }

    # Map interaction scores to a new column
    scores = interactions_df.copy()
    scores['InteractionScore'] = scores['interaction_type'].map(score_map).fillna(0)

    # Group by UserID and ContentID, resolving conflicts
    def resolve_scores(group):
        scoreslist = group['InteractionScore'].tolist()
        if any(score < 0 for score in scoreslist):  # If any negative interaction exists
            return max(filter(lambda x: x < 0, scoreslist))  # Return highest negative score
        else:
            return max(scoreslist)  # Return highest positive score

    # Resolve scores for each user-item pair
    scores = scores.groupby(['user_id', 'content_id']).apply(resolve_scores).reset_index()
    scores.rename(columns={0: 'ResolvedScore'}, inplace=True)

    # Keep the structure for future merges
    return scores

def assign_interest_scores(user_df, content_df, resolved_scores_df):
    """
    Assign a score of 1 to user-content pairs based on interest matching.
    Updates the resolved_scores_df for missing scores.
    
    Parameters:
        user_df (pd.DataFrame): User data with 'UserID' and 'liked_cat' columns.
        content_df (pd.DataFrame): Content data with 'ContentID' and 'categories' columns.
        resolved_scores_df (pd.DataFrame): Existing resolved scores with 'UserID', 'ContentID', and 'ResolvedScore'.
        
    Returns:
        pd.DataFrame: Updated resolved_scores_df with new scores assigned for interest matches.
    """
    # Convert the resolved_scores_df to a set of user-content pairs for quick lookup
    existing_pairs = set(zip(resolved_scores_df['user_id'], resolved_scores_df['content_id']))
    
    # List to store new rows
    new_scores = []
    
    # Iterate over all possible user-content pairs
    for _, user_row in user_df.iterrows():
        user_id = user_row['user_id']
        liked_cat = set(user_row['liked_cat'].split(','))  # Assuming liked_cat is comma-separated
        
        for _, content_row in content_df.iterrows():
            content_id = content_row['content_id']
            categories = set(content_row['categories'].split(','))  # Assuming categories is comma-separated
            
            # Check if the pair already has a score
            if (user_id, content_id) not in existing_pairs:
                # Check for an interest match
                if liked_cat & categories:  # Intersection of sets
                    new_scores.append({'user_id': user_id, 'content_id': content_id, 'ResolvedScore': 1})
    
    # Create a DataFrame for new scores and append to the existing resolved_scores_df
    new_scores_df = pd.DataFrame(new_scores)
    updated_scores_df = pd.concat([resolved_scores_df, new_scores_df], ignore_index=True)
    
    return updated_scores_df


def main():
    """Main function of the script."""

    # input and output arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--interactions", 
        type=str, 
        help="path to input data")
    parser.add_argument(
        "--processed_interactions", 
        type=str, 
        required=True, 
        help="Processed interaction data")
    args = parser.parse_args()

    # Start Logging
    mlflow.start_run()
    print(" ".join(f"{k}={v}" for k, v in vars(args).items()))
    print("input data:", args.interactions)

    interactions_df = pd.read_csv(args.interactions, header=0, index_col=0)
    print(interactions_df.tail(10))

    processed_interactions_df = score_interactions(interactions_df)

    mlflow.log_metric("num_samples", processed_interactions_df.shape[0])
    mlflow.log_metric("num_features", processed_interactions_df.shape[1] - 1)

    processed_interactions_path = args.processed_interactions
    os.makedirs(processed_interactions_path, exist_ok=True)

    processed_interactions = os.path.join(processed_interactions_path, 'processed_interactions.csv')
    processed_interactions_df.to_csv(processed_interactions, index=False)

    # Stop Logging
    mlflow.end_run()


if __name__ == "__main__":
    main()
