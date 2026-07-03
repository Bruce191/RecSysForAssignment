import pandas as pd
import numpy as np
import ast
import os
import argparse
import mlflow

def select_first_file(path):
    """Selects first file in folder, use under assumption there is only one file in folder
    Args:
        path (str): path to directory or file to choose
    Returns:
        str: full path of selected file
    """
    files = os.listdir(path)
    return os.path.join(path, files[0])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all_recommendations", 
        type=str, 
        help="path to the recommendations")
    parser.add_argument(
        "--content", 
        type=str, 
        help="path to content data")
    parser.add_argument(
        "--merged_recommendations", 
        type=str, 
        help="path for storing merged recommendations")
    args = parser.parse_args()

    mlflow.start_run()
    print(" ".join(f"{k}={v}" for k, v in vars(args).items()))
    print("input data:", args.all_recommendations)

    all_recommendations_df = pd.read_csv(select_first_file(args.all_recommendations), index_col=0, header=0).reset_index(drop=False)
    print(all_recommendations_df.head())

    content_df = pd.read_csv(args.content, header=0)
    print(content_df.head())

    all_recommendations_df['Recommendations'] = all_recommendations_df['Recommendations'].apply(ast.literal_eval)
    all_recommendations_df = all_recommendations_df.explode("Recommendations")
    #recommendations_exploded = all_recommendations_df.explode('Recommendations', ignore_index=True)
    all_recommendations_df = all_recommendations_df.rename(
        columns={'Recommendations': 'content_id'})

    merged_recommendations_df = pd.merge(
        all_recommendations_df, 
        content_df, 
        on='content_id', 
        how='left')

    print(merged_recommendations_df.columns)
    #merged_recommendations_df = merged_recommendations_df.dropna()
    print(merged_recommendations_df.isnull().sum().any())
    print(len(merged_recommendations_df))

    mlflow.log_metric("num_samples", merged_recommendations_df.shape[0])
    mlflow.log_metric("num_features", merged_recommendations_df.shape[1] - 1)

    merged_recommendations_path = args.merged_recommendations
    os.makedirs(merged_recommendations_path, exist_ok=True)

    merged_recommendations = os.path.join(merged_recommendations_path, "merged_recommendations.csv")
    merged_recommendations_df.to_csv(merged_recommendations, index=False)

    mlflow.end_run()

if __name__ == "__main__":
    main()
