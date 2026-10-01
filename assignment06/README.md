# Assignment 06 – Multimodal Search System for E-Commerce (prototype)

Student: KHANHBQ (049), class 04.

A three-layer Python prototype. Text, voice and image inputs all become one common
query object, and then go through the same steps: retrieval, ranking, results.

## Requirements

* Python 3.9+ (tested with 3.14.4)
* `numpy` (tested 2.4.6), `pillow` (tested 12.3.0)

```bash
pip install numpy pillow
# or, without installing anything globally:
uv run --no-project --with numpy --with pillow python main.py
```

## How to run

```bash
cd assignment06
python main.py                                   # full demo: text, voice, image, text+image, orders
python evaluate.py                               # 20-query test set + success rate
python tools/make_images.py                      # (re)generate sample product / query images
```

Example commands:

```bash
python main.py --text "black shoes"
python main.py --text "find Nike shoes under 100 dollars"
python main.py --voice "find running shoes"                      # simulated speech-to-text
python main.py --image data/query_images/query_black_shoe.png
python main.py --text "running shoes" --image data/query_images/query_red_shoe.png --weight 0.5
python main.py --text "find my order O001"
python main.py --voice "where is my latest order" --customer C001
```

## Directory structure

```
assignment06/
├── main.py                      wiring + demo / CLI
├── evaluate.py                  test set, success rate
├── presentation/
│   └── search_ui.py             SearchUI, VoiceInput, ImageUpload, SearchResultView
├── application/
│   ├── query_service.py         input -> common query object (terms, filters, embedding)
│   ├── speech_service.py        speech-to-text (SIMULATED)
│   ├── image_service.py         image encoder f(I): colour histogram + shape grid (128-d)
│   ├── search_service.py        retrieval: keyword matching, vector similarity, orders
│   └── ranking_service.py       S = a*S_text + b*S_image + g*S_business
├── data/
│   ├── product_repository.py    ProductRepository (reads products.json)
│   ├── order_repository.py      OrderRepository (Order Database, in memory)
│   ├── vector_index.py          VectorIndex + cosine similarity
│   ├── image_storage.py         ImageStorage (image files)
│   ├── products.json            12 products (product dataset)
│   ├── images/                  product images
│   └── query_images/            query "photos" used for image search
└── tools/make_images.py         generator of the sample images
```

Only the presentation layer calls application services, and only application services call
repositories. The UI never reads `products.json` itself.

## Limitations of the prototype

* **Speech recognition is simulated.** `SpeechService.transcribe()` gets the sentence that a
  speech-to-text engine would return. A real engine (e.g. Whisper) can be plugged in there.
* The image encoder is hand-made (colour histogram + 8x8 shape grid), not a neural network.
  It recognises colour and silhouette, not brand or fine details. Two products with the same
  picture (e.g. two white shoes) get the same score, and stock decides the order.
* The sample images are synthetic drawings made by `tools/make_images.py`, not real photos.
* Keyword matching uses exact tokens with a light plural rule. It has no synonyms
  ("sneakers" is not "shoes") and no typo tolerance.
* Data lives in a JSON file / in memory, and the vector index is a brute-force dictionary.
