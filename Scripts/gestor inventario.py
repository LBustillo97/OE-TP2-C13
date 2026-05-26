import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Rutas a los archivos CSV
PRODUCTS_CSV = Path("./Datos/BASE DE DATOS PRODUCTOS.csv")
SALES_CSV = Path("./Datos/BASE DE DATOS VENTA PRODUCTOS.csv")

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

if __name__ == "__main__":
    from pathlib import Path

    print("Directorio de trabajo:", Path.cwd())
    print("PRODUCTS_CSV:", PRODUCTS_CSV.resolve())
    print("SALES_CSV:", SALES_CSV.resolve())

    # Cargar datos con manejo de errores
    try:
        products, sales = load_data()
    except Exception as e:
        print("Error al cargar datos:", e)
        input("Presiona Enter para salir...")
        raise

    def safe_show(fig_name=None):
        try:
            plt.show()
        except Exception:
            if fig_name:
                plt.savefig(fig_name, bbox_inches='tight')
                print(f"Gráfico guardado en {fig_name}")
            else:
                print("No se pudo mostrar el gráfico; use plt.savefig() para guardar.")

    def input_int(prompt, allow_empty=False):
        while True:
            val = input(prompt)
            if allow_empty and val.strip()=="":
                return None
            try:
                return int(val)
            except ValueError:
                print("Ingrese un número entero válido.")

    def input_float(prompt, allow_empty=False):
        while True:
            val = input(prompt)
            if allow_empty and val.strip()=="":
                return None
            try:
                return float(val)
            except ValueError:
                print("Ingrese un número válido (ej: 12500).")

    def add_product_interactive():
        print("Agregar producto")
        idp = input_int("id_producto: ")
        nombre = input("producto (nombre): ").strip()
        precio = input_float("precio: ")
        try:
            nonlocal_products = add_product(products, idp, nombre, precio)
            return nonlocal_products
        except Exception as e:
            print("Error al agregar producto:", e)
            return products

    def update_product_interactive():
        print("Actualizar producto")
        idp = input_int("id_producto a actualizar: ")
        if idp not in products['id_producto'].values:
            print("id_producto no encontrado.")
            return products
        nombre = input("Nuevo nombre (enter para no cambiar): ").strip()
        precio = input("Nuevo precio (enter para no cambiar): ").strip()
        fields = {}
        if nombre != "":
            fields['producto'] = nombre
        if precio != "":
            try:
                fields['precio'] = float(precio)
            except ValueError:
                print("Precio inválido, no se actualizará ese campo.")
        try:
            return update_product(products, idp, **fields)
        except Exception as e:
            print("Error al actualizar:", e)
            return products

    def delete_product_interactive():
        print("Eliminar producto")
        idp = input_int("id_producto a eliminar: ")
        confirm = input(f"Confirma eliminar producto {idp}? (s/n): ").lower()
        if confirm == 's':
            return delete_product(products, idp)
        print("Eliminación cancelada.")
        return products

    def add_sale_interactive():
        print("Agregar venta")
        fecha = input("fecha (YYYY-MM-DD): ").strip()
        idv = input_int("id_venta: ")
        idp = input_int("id_producto: ")
        product0 = input("product0 (nombre producto): ").strip()
        cantidad = input_int("cantidad: ")
        precio_unitario = input_float("precio_unitario: ")
        try:
            nonlocal_sales = add_sale(sales, fecha, idv, idp, product0, cantidad, precio_unitario)
            return nonlocal_sales
        except Exception as e:
            print("Error al agregar venta:", e)
            return sales

    def update_sale_interactive():
        print("Actualizar venta")
        idv = input_int("id_venta a actualizar: ")
        if idv not in sales['id_venta'].values:
            print("id_venta no encontrado.")
            return sales
        # Pedir campos opcionales
        fecha = input("Nueva fecha (enter para no cambiar): ").strip()
        cantidad = input("Nueva cantidad (enter para no cambiar): ").strip()
        precio_unitario = input("Nuevo precio_unitario (enter para no cambiar): ").strip()
        fields = {}
        if fecha != "":
            fields['fecha'] = pd.to_datetime(fecha)
        if cantidad != "":
            try:
                fields['cantidad'] = int(cantidad)
            except ValueError:
                print("Cantidad inválida; no se actualizará.")
        if precio_unitario != "":
            try:
                fields['precio_unitario'] = float(precio_unitario)
            except ValueError:
                print("Precio inválido; no se actualizará.")
        try:
            return update_sale(sales, idv, **fields)
        except Exception as e:
            print("Error al actualizar venta:", e)
            return sales

    def delete_sale_interactive():
        print("Eliminar venta")
        idv = input_int("id_venta a eliminar: ")
        confirm = input(f"Confirma eliminar venta {idv}? (s/n): ").lower()
        if confirm == 's':
            return delete_sale(sales, idv)
        print("Eliminación cancelada.")
        return sales

    # Menú principal
    while True:
        print("\n--- Menú principal ---")
        print("1 - Listar productos")
        print("2 - Agregar producto")
        print("3 - Actualizar producto")
        print("4 - Eliminar producto")
        print("5 - Listar ventas")
        print("6 - Agregar venta")
        print("7 - Actualizar venta")
        print("8 - Eliminar venta")
        print("9 - Mostrar gráfico: cantidad vendida por producto")
        print("10 - Mostrar gráfico: ingresos por producto")
        print("11 - Mostrar gráfico: ingresos por fecha")
        print("12 - Guardar cambios en CSV")
        print("0 - Salir")
        try:
            opt = int(input("> "))
        except ValueError:
            print("Ingrese una opción válida.")
            continue

        if opt == 0:
            print("Saliendo...")
            break
        elif opt == 1:
            print(products.to_string(index=False))
        elif opt == 2:
            products = add_product_interactive()
        elif opt == 3:
            products = update_product_interactive()
        elif opt == 4:
            products = delete_product_interactive()
        elif opt == 5:
            print(sales.to_string(index=False))
        elif opt == 6:
            sales = add_sale_interactive()
        elif opt == 7:
            sales = update_sale_interactive()
        elif opt == 8:
            sales = delete_sale_interactive()
        elif opt == 9:
            plot_sales_by_product(sales, products)
            safe_show("ventas_por_producto.png")
        elif opt == 10:
            plot_revenue_by_product(sales)
            safe_show("ingresos_por_producto.png")
        elif opt == 11:
            plot_revenue_over_time(sales)
            safe_show("ingresos_por_fecha.png")
        elif opt == 12:
            try:
                save_data(products, sales)
                print("Cambios guardados en CSV.")
            except Exception as e:
                print("Error al guardar:", e)
        else:
            print("Opción no reconocida.")

    input("Presiona Enter para terminar...")

