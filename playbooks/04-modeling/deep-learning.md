# Playbook: Deep Learning & LLMs

## When to Use

- Input is unstructured: text, images, audio, video, sequences
- Tabular data with >100k rows where tree methods have plateaued
- LLM-based: classification, extraction, summarization, generation, RAG

## Frameworks

| Use case | Framework |
|---|---|
| General deep learning | PyTorch |
| LLM inference & fine-tuning | HuggingFace Transformers + PEFT/LoRA |
| LLM APIs (Claude, GPT) | Anthropic SDK / OpenAI SDK |
| Embeddings & vector search | sentence-transformers, FAISS, ChromaDB |

## Checklist — General DL

- [ ] Start with a pretrained model; fine-tune rather than train from scratch
- [ ] Implement early stopping and checkpoint the best epoch
- [ ] Log loss curves (train vs. val) to catch over/underfitting
- [ ] Use mixed precision (`torch.cuda.amp`) if training on GPU
- [ ] Profile memory usage before scaling batch size
- [ ] Save model with `torch.save` or `model.save_pretrained()`

## Checklist — LLM / Prompt Engineering

- [ ] Define eval criteria before writing prompts (what does "good" look like?)
- [ ] Version prompts as code — store in `src/prompts/`
- [ ] Test prompts against a fixed eval set; don't eyeball
- [ ] Cache API responses during development to avoid cost/latency
- [ ] Log token usage per call for cost tracking
- [ ] For RAG: chunk size, overlap, and retrieval k are hyperparameters — tune them

## Notes

<!-- Add project-specific notes here -->
