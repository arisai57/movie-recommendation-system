import math
import re
from collections import Counter
from pathlib import Path


def read_document_list(list_path: Path):
    if not list_path.exists():
        raise FileNotFoundError(f"Document list file not found: {list_path}")
    lines = [line.strip().lstrip("\ufeff") for line in list_path.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]


def read_stopwords(stopwords_path: Path):
    if not stopwords_path.exists():
        return set()
    lines = [line.strip().lstrip("\ufeff").lower() for line in stopwords_path.read_text(encoding="utf-8").splitlines()]
    return {line for line in lines if line}


def clean_text(text: str) -> str:
    # Remove URLs first
    text = re.sub(r"https?://\S+", " ", text)
    # Remove apostrophes
    text = text.replace("'", "")
    # Keep only letters, digits, underscores and whitespace
    text = re.sub(r"[^A-Za-z0-9_\s]+", " ", text)
    # Normalize whitespace and lowercase
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def stem_word(word: str) -> str:
    if len(word) > 3 and word.endswith("ing"):
        return word[:-3]
    if len(word) > 2 and word.endswith("ly"):
        return word[:-2]
    if len(word) > 4 and word.endswith("ment"):
        return word[:-4]
    return word


def preprocess_words(text: str, stopwords: set[str]) -> list[str]:
    cleaned = clean_text(text)
    if not cleaned:
        return []
    words = cleaned.split(" ")
    processed = []
    for word in words:
        if not word or word in stopwords:
            continue
        stemmed = stem_word(word)
        if stemmed:
            processed.append(stemmed)
    return processed


def write_preproc_file(doc_name: str, words: list[str], out_dir: Path):
    output_name = f"preproc_{Path(doc_name).name}"
    output_path = out_dir / output_name
    output_path.write_text(" ".join(words), encoding="utf-8")
    return output_path


def compute_tfidf_for_documents(preproc_paths: list[Path]):
    all_docs_words = []
    for preproc_path in preproc_paths:
        text = preproc_path.read_text(encoding="utf-8").strip()
        words = text.split() if text else []
        all_docs_words.append(words)

    num_docs = len(all_docs_words)
    doc_counts = Counter()
    for words in all_docs_words:
        doc_counts.update(set(words))

    tfidf_results = []
    for words in all_docs_words:
        total_terms = len(words)
        if total_terms == 0:
            tfidf_results.append([])
            continue
        freq = Counter(words)
        doc_scores = []
        for word, count in freq.items():
            tf = count / total_terms
            idf = math.log(num_docs / doc_counts[word]) + 1
            score = round(tf * idf, 2)
            doc_scores.append((word, score))
        doc_scores.sort(key=lambda item: (-item[1], item[0]))
        tfidf_results.append(doc_scores[:5])
    return tfidf_results


def format_tfidf_list(tuples: list[tuple[str, float]]) -> str:
    formatted = [f"({repr(word)}, {score:.2f})" for word, score in tuples]
    return f"[{', '.join(formatted)}]"


def write_tfidf_file(doc_name: str, top_words: list[tuple[str, float]], out_dir: Path):
    output_name = f"tfidf_{Path(doc_name).name}"
    output_path = out_dir / output_name
    output_path.write_text(format_tfidf_list(top_words), encoding="utf-8")
    return output_path


def main():
    base_dir = Path.cwd()
    docs_list_path = base_dir / "tfidf_docs.txt"
    stopwords_path = base_dir / "stopwords.txt"

    try:
        document_names = read_document_list(docs_list_path)
    except FileNotFoundError as exc:
        print(exc)
        return

    stopwords = read_stopwords(stopwords_path)
    preproc_paths = []

    for doc_name in document_names:
        doc_name = doc_name.lstrip("\ufeff")
        doc_path = base_dir / doc_name
        if not doc_path.exists():
            print(f"Warning: input document not found: {doc_name}")
            empty_preproc = base_dir / f"preproc_{Path(doc_name).name}"
            empty_preproc.write_text("", encoding="utf-8")
            preproc_paths.append(empty_preproc)
            continue
        text = doc_path.read_text(encoding="utf-8")
        words = preprocess_words(text, stopwords)
        out_path = write_preproc_file(doc_name, words, base_dir)
        preproc_paths.append(out_path)

    tfidf_results = compute_tfidf_for_documents(preproc_paths)
    for doc_name, top_words in zip(document_names, tfidf_results):
        write_tfidf_file(doc_name, top_words, base_dir)


if __name__ == "__main__":
    main()
