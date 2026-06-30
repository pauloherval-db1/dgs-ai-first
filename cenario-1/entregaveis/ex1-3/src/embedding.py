from langchain_huggingface import HuggingFaceEmbeddings


def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
