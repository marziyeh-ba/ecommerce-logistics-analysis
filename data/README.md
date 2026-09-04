# Source data

This project uses the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). The source files are not committed because they are distributed by the dataset owner.

Download the dataset and place these files in `data/raw/`:

```text
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_order_reviews_dataset.csv
olist_products_dataset.csv
product_category_name_translation.csv
olist_sellers_dataset.csv
olist_order_payments_dataset.csv
```

Expected layout:

```text
data/
├── README.md
└── raw/
    ├── olist_orders_dataset.csv
    ├── olist_order_items_dataset.csv
    ├── olist_order_reviews_dataset.csv
    ├── olist_products_dataset.csv
    ├── product_category_name_translation.csv
    ├── olist_sellers_dataset.csv
    └── olist_order_payments_dataset.csv
```

The notebook validates these filenames before loading any data and reports missing files clearly.
