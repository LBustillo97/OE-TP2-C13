import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Rutas a los archivos CSV
PRODUCTS_CSV = Path("Datos/BASE DE DATOS PRODUCTOS.csv")
SALES_CSV = Path("Datos/BASE DE DATOS VENTA PRODUCTOS.csv")

# Cargar datos (delimitador ;)
def load_data():
    products = pd.read_csv(PRODUCTS_CSV, sep=';', dtype={'id_producto':int, 'producto':str, 'precio':float})
    sales = pd.read_csv(SALES_CSV, sep=';', dtype={'id_venta':int, 'id_producto':int, 'product0':str, 'cantidad':int, 'precio_unitario':float, 'total':float}, parse_dates=['fecha'])
    return products, sales

# Guardar cambios
def save_data(products, sales):
    products.to_csv(PRODUCTS_CSV, sep=';', index=False)
    sales.to_csv(SALES_CSV, sep=';', index=False)

# Operaciones CRUD sobre productos
def add_product(products, id_producto, producto, precio):
    if id_producto in products['id_producto'].values:
        raise ValueError("id_producto ya existe")
    new = pd.DataFrame([{'id_producto':id_producto, 'producto':producto, 'precio':precio}])
    return pd.concat([products, new], ignore_index=True)

def update_product(products, id_producto, **fields):
    idx = products.index[products['id_producto']==id_producto]
    if idx.empty:
        raise ValueError("Producto no encontrado")
    for k,v in fields.items():
        if k in products.columns:
            products.loc[idx, k] = v
    return products

def delete_product(products, id_producto):
    return products[products['id_producto']!=id_producto].reset_index(drop=True)

# Operaciones CRUD sobre ventas
def add_sale(sales, fecha, id_venta, id_producto, product0, cantidad, precio_unitario):
    if id_venta in sales['id_venta'].values:
        raise ValueError("id_venta ya existe")
    total = cantidad * precio_unitario
    new = pd.DataFrame([{
        'fecha': pd.to_datetime(fecha),
        'id_venta': id_venta,
        'id_producto': id_producto,
        'product0': product0,
        'cantidad': cantidad,
        'precio_unitario': precio_unitario,
        'total': total
    }])
    return pd.concat([sales, new], ignore_index=True)

def update_sale(sales, id_venta, **fields):
    idx = sales.index[sales['id_venta']==id_venta]
    if idx.empty:
        raise ValueError("Venta no encontrada")
    for k,v in fields.items():
        if k in sales.columns:
            sales.loc[idx, k] = v
    # recalcular total si cambian cantidad o precio_unitario
    if 'cantidad' in fields or 'precio_unitario' in fields:
        sales.loc[idx, 'total'] = sales.loc[idx, 'cantidad'] * sales.loc[idx, 'precio_unitario']
    return sales

def delete_sale(sales, id_venta):
    return sales[sales['id_venta']!=id_venta].reset_index(drop=True)

# Gráficos
def plot_sales_by_product(sales, products):
    df = sales.groupby('product0', as_index=False).agg({'cantidad':'sum', 'total':'sum'}).sort_values('cantidad', ascending=False)
    plt.figure(figsize=(10,6))
    sns.barplot(data=df, x='cantidad', y='product0', palette='viridis')
    plt.title('Cantidad vendida por producto')
    plt.xlabel('Cantidad total vendida')
    plt.ylabel('Producto')
    plt.tight_layout()
    plt.show()

def plot_revenue_by_product(sales):
    df = sales.groupby('product0', as_index=False).agg({'total':'sum'}).sort_values('total', ascending=False)
    plt.figure(figsize=(10,6))
    sns.barplot(data=df, x='total', y='product0', palette='magma')
    plt.title('Ingresos por producto')
    plt.xlabel('Ingresos totales')
    plt.ylabel('Producto')
    plt.tight_layout()
    plt.show()

def plot_revenue_over_time(sales):
    df = sales.groupby('fecha', as_index=False).agg({'total':'sum'}).sort_values('fecha')
    plt.figure(figsize=(10,5))
    sns.lineplot(data=df, x='fecha', y='total', marker='o')
    plt.title('Evolución de ingresos por fecha')
    plt.xlabel('Fecha')
    plt.ylabel('Ingresos totales')
    plt.tight_layout()
    plt.show()

# Ejemplo de uso
if __name__ == "__main__":
    products, sales = load_data()

    # Mostrar primeras filas
    print("Productos:")
    print(products.head())
    print("\nVentas:")
    print(sales.head())

    # Graficar
    plot_sales_by_product(sales, products)
    plot_revenue_by_product(sales)
    plot_revenue_over_time(sales)

    # Ejemplo de edición: agregar un producto y una venta
    # products = add_product(products, 21, 'nuevo_producto', 12345)
    # sales = add_sale(sales, '2026-05-06', 1016, 21, 'nuevo_producto', 2, 12345)
    # save_data(products, sales)
