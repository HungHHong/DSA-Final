from src.preprocess import load_data, merge_movie_tags

def looks_broken(tag):
    if not isinstance(tag, str):
        return False
    return any(broken in tag for broken in ['Ã', 'â', '�', '¢', '¤', '€', 'ð', 'Ã©', 'Ãª', 'Ã£'])

def try_fix(tag):
    try:
        return tag.encode('latin1').decode('utf-8')
    except:
        return None

def main():
    # Load the data with initial fixes
    ratings, movies, tags = load_data()

    # 🔍 Detect broken tags
    broken_tags = tags[tags['tag'].apply(looks_broken)]
    print("\n--- Suspected Broken Tags ---")
    print(broken_tags[['movieId', 'tag']].drop_duplicates().sort_values(by='movieId'))

    # 🛠 Generate and show fix suggestions
    broken_unique = broken_tags['tag'].unique()
    corrupted_map = {
        tag: try_fix(tag)
        for tag in broken_unique
        if try_fix(tag) and try_fix(tag) != tag
    }

    print("\n--- Suggested Fixes ---")
    for broken, fixed in corrupted_map.items():
        print(f"'{broken}' -> '{fixed}'")

    # 🧩 Merge cleaned tags with movies
    movies_with_tags = merge_movie_tags(movies, tags)

    # 📋 Preview
    print("\n--- Sample Movies with Tags ---")
    print(movies_with_tags.head())

    print("\n--- Tags for movieId 3 ---")
    print(movies_with_tags[movies_with_tags['movieId'] == 3])

if __name__ == '__main__':
    main()




# import chardet
#
# file_path = "C:/Users/Hung Hong/Documents/GitHub/DSA-Final/data/tags.csv"
#
# with open(file_path, 'rb') as f:
#     raw = f.read()
#
# print(raw[:1000])  # print the first 1000 bytes
