import pandas as pd

def extract_data(
        orders_file:str="ordres.csv",
        customers_file:str="customers.csv",
        products_file:str="products.csv"
):
    orders=pd.read_csv(f"data/raw/{orders_file}")
    customers=pd.read_csv(f"data/raw/{customers_file}")
    products=pd.read_csv(f"data/raw/{products_file}")

    print("\nExtract completed!")
    # print(f"Orders data shape:{orders.shape}")
    # print(f"Customers data shape:{customers.shape}")
    # print(f"Products data shape:{products.shape}")
    
    return orders, customers, products

if __name__ == "__main__":
    extract_data()