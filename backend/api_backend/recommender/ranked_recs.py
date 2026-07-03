import pandas as pd
import numpy as np
import ast
import os
import argparse
import mlflow

def downrank_pc_ndc_content(df, remove_or_rerank='rerank', apply_to_all=False):
    results = pd.DataFrame(columns=df.columns)
    unique_users = df['user_id'].unique()

    for user in unique_users:
        user_recs = df[df['user_id'] == user]
        rows_to_keep = []
        rows_to_rerank = []

        for i in range(len(user_recs)):
            harm_class = user_recs.iloc[i].get('harms_classification')
            is_child = user_recs.iloc[i].get('is_child')

            target = harm_class in ['PC', 'NDC']
            condition = apply_to_all or (is_child is True)

            if target and condition:
                if remove_or_rerank == 'remove':
                    continue
                elif remove_or_rerank == 'rerank':
                    rows_to_rerank.append(user_recs.iloc[i])
            else:
                rows_to_keep.append(user_recs.iloc[i])

        updated_recs = pd.DataFrame(rows_to_keep + rows_to_rerank, columns=df.columns)
        results = pd.concat([results, updated_recs], ignore_index=True)

    return results

def filter_ppc_content(df, remove_or_rerank='remove', apply_to_all=True):
    results = pd.DataFrame(columns=df.columns)
    unique_users = df['user_id'].unique()

    for user in unique_users:
        user_recs = df[df['user_id'] == user]
        rows_to_keep = []
        rows_to_rerank = []

        for i in range(len(user_recs)):
            harm_class = user_recs.iloc[i].get('HarmCategoryClassification')
            is_child = user_recs.iloc[i].get('is_child')

            target = harm_class == 'PPC'
            condition = apply_to_all or (is_child is True)

            if target and condition:
                if remove_or_rerank == 'remove':
                    continue
                elif remove_or_rerank == 'rerank':
                    rows_to_rerank.append(user_recs.iloc[i])
            else:
                rows_to_keep.append(user_recs.iloc[i])

        updated_recs = pd.DataFrame(rows_to_keep + rows_to_rerank, columns=df.columns)
        results = pd.concat([results, updated_recs], ignore_index=True)

    return results

#TODO this has to be fixed once liked sub categories are recorded for users
def uprank_liked_categories(df):
    results = pd.DataFrame(columns=df.columns)
    unique_users = df['user_id'].unique()

    for user in unique_users:
        user_recs = df[df['user_id'] == user]
        liked_rows = []
        other_rows = []

        for i in range(len(user_recs)):
            article_category = user_recs.iloc[i]['sub_category']
            user_liked_cat = user_recs.iloc[i]['liked_cat']

            if article_category == user_liked_cat:
                liked_rows.append(user_recs.iloc[i])
            else:
                other_rows.append(user_recs.iloc[i])

        rearranged_recs = pd.DataFrame(liked_rows + other_rows, columns=df.columns)
        results = pd.concat([results, rearranged_recs], ignore_index=True)

    return results

def select_first_file(path):
    files = os.listdir(path)
    return os.path.join(path, files[0])

def blockwise_shuffle(df, block_size=5, seed=None):
    if seed is not None:
        np.random.seed(seed)

    num_blocks = len(df) // block_size
    blocks = [df.iloc[i * block_size : (i + 1) * block_size] for i in range(num_blocks)]
    np.random.shuffle(blocks)
    shuffled_df = pd.concat(blocks, ignore_index=True)

    return shuffled_df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--merged_recommendations", type=str, help="path to the merged recommendations")
    parser.add_argument("--ranked_recommendations", type=str, help="path for storing ranked recommendations")
    args = parser.parse_args()

    mlflow.start_run()
    print(" ".join(f"{k}={v}" for k, v in vars(args).items()))
    print("input data:", args.merged_recommendations)

    merged_recommendations_df = pd.read_csv(select_first_file(args.merged_recommendations))
    print(merged_recommendations_df.head())

    # Apply filtering and re-ranking
    df = downrank_pc_ndc_content(merged_recommendations_df)  # PC + NDC for children only
    df = filter_ppc_content(df)                              # PPC for everyone
    #df = uprank_liked_categories(df)                         # Liked categories to top

    print('These are the reranked_recommendations')
    print(df.head())
    print(df.columns)

    mlflow.log_metric("num_samples", df.shape[0])
    mlflow.log_metric("num_features", df.shape[1] - 1)

    output_dir = args.ranked_recommendations
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "ranked_recommendations.csv"), index=False)

    mlflow.end_run()

if __name__ == "__main__":
    main()
