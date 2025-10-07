import csv
from django.http import HttpResponse
from rangefilter.filters import DateRangeFilter
from django.contrib import admin

from inventory.models import (
    Brand,
    Category,
    Product,
    Purchase,
    PurchaseItem,
    SaleInvoice,
    SaleInvoiceItem,
    Provider,
    CashFlow,
)

admin.site.register(Brand)
admin.site.register(Provider)


# region Category admin
def export_categories_as_csv(modeladmin, request, queryset):
    """
    Exportar registros seleccionados a CSV
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="categorias.csv"'
    writer = csv.writer(response)

    # Escribir encabezados
    writer.writerow(
        [
            "ID",
            "Nombre",
            "Descripcion",
        ]
    )

    # Escribir filas
    for obj in queryset:
        writer.writerow(
            [
                obj.id,
                obj.name,
                obj.description,
            ]
        )
    return response


export_categories_as_csv.short_description = "Exportar seleccionados a CSV"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
    )
    list_filter = ()
    search_fields = ("id", "name", "description")
    actions = [export_categories_as_csv]


# region Purchase admin
def export_purchases_as_csv(modeladmin, request, queryset):
    """
    Exportar registros seleccionados a CSV
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="compras.csv"'
    writer = csv.writer(response)

    # Escribir encabezados
    writer.writerow(
        [
            "ID",
            "Encargado de compra",
            "Proveedor",
            "Fecha y hora de compra",
            "Total",
            "Anulado",
        ]
    )

    # Escribir filas
    for obj in queryset:
        writer.writerow(
            [
                obj.id,
                obj.user.username,
                obj.provider,
                obj.purchase_date.strftime("%Y-%m-%d %H:%M:%S"),
                obj.total,
                "SI" if obj.voided else "NO",
            ]
        )
    return response


export_purchases_as_csv.short_description = "Exportar seleccionados a CSV"


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "provider",
        "purchase_date",
        "total",
        "voided",
    )
    list_filter = (("purchase_date", DateRangeFilter), "user", "provider", "voided")
    search_fields = (
        "id",
        "user__username",
        "provider__name",
    )
    actions = [export_purchases_as_csv]


# region PurchaseItem admin
def export_purchase_item_as_csv(modeladmin, request, queryset):
    """
    Exportar registros seleccionados a CSV
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="detalle_compras.csv"'
    writer = csv.writer(response)

    # Escribir encabezados
    writer.writerow(
        [
            "ID",
            "Producto ID",
            "Producto Nombre",
            "Producto Categoria",
            "Producto Marca",
            "Compra ID",
            "Encargado de compra",
            "Fecha y hora de compra",
            "Cantidad comprada",
            "Precio de compra",
            "Subtotal",
            "Anulado",
        ]
    )

    # Escribir filas
    for obj in queryset:
        writer.writerow(
            [
                obj.id,
                obj.product.id,
                obj.product.name,
                obj.product.category.name,
                obj.product.brand.name,
                obj.purchase.id,
                obj.purchase.user.username,
                obj.purchase_date.strftime("%Y-%m-%d %H:%M:%S"),
                obj.quantity,
                obj.price,
                obj.subtotal,
                "SI" if obj.purchase.voided else "NO",
            ]
        )
    return response


export_purchase_item_as_csv.short_description = "Exportar seleccionados a CSV"


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_id",
        "product_name",
        "product_category_name",
        "product_brand_name",
        "purchase_id",
        "purchase_user_username",
        "purchase_date",
        "quantity",
        "price",
        "subtotal",
        "purchase_voided",
    )
    list_filter = (("purchase_date", DateRangeFilter), "purchase__voided")
    search_fields = (
        "id",
        "user__username",
        "provider__name",
        "product__name",
        "product__category__name",
        "product__brand__name",
    )
    actions = [export_purchase_item_as_csv]

    # ----- Custom column methods -----
    def product_name(self, obj):
        return obj.product.name

    product_name.short_description = "Producto"

    def product_category_name(self, obj):
        return obj.product.category.name

    product_category_name.short_description = "Categoría"

    def product_brand_name(self, obj):
        return obj.product.brand.name

    product_brand_name.short_description = "Marca"

    def purchase_user_username(self, obj):
        return obj.purchase.user.username

    purchase_user_username.short_description = "Usuario"

    def purchase_voided(self, obj):
        return obj.purchase.voided

    purchase_voided.short_description = "Compra Padre Anulada"
    purchase_voided.boolean = True


# region Product admin
def export_products_as_csv(modeladmin, request, queryset):
    """
    Exportar registros seleccionados a CSV
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="productos.csv"'
    writer = csv.writer(response)

    # Escribir encabezados
    writer.writerow(
        [
            "ID",
            "Nombre",
            "Descripcion",
            "Marca",
            "Categoria",
            "Precio de Venta",
            "Existencias",
            "Tipo de Inventario",
            "Minimo de existencias permitido",
            "Abastecido",
        ]
    )

    # Escribir filas
    for obj in queryset:
        writer.writerow(
            [
                obj.id,
                obj.name,
                obj.description,
                obj.brand.name,
                obj.category.name,
                obj.sale_price,
                obj.stock,
                obj.get_inventory_type_display(),
                obj.min_threshold,
                "SI" if obj.supplied else "NO",
            ]
        )
    return response


export_products_as_csv.short_description = "Exportar seleccionados a CSV"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "brand",
        "category",
        "sale_price",
        "stock",
        "inventory_type",
        "min_threshold",
        "supplied",
    )
    list_filter = ("inventory_type", "brand", "category", "supplied")
    search_fields = ("name", "description")
    actions = [export_products_as_csv]  # 👈 aquí registramos la acción


# region SaleInvoiceItem
def export_sale_item_as_csv(modeladmin, request, queryset):
    """Export selected records to CSV"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="sale_invoice_items.csv"'
    writer = csv.writer(response)

    # Headers
    writer.writerow(
        [
            "ID",
            "Venta ID",
            "Producto ID",
            "Producto Nombre",
            "Producto Categoria",
            "Producto Marca",
            "Precio de Venta",
            "Cantidad",
            "Subtotal",
            "Fecha de venta",
            "Encargado de Venta",
            "Tipo de Venta",
            "Venta Padre Anulada",
        ]
    )

    # Rows
    for obj in queryset.iterator():
        writer.writerow(
            [
                obj.id,
                obj.sale_invoice.id,
                obj.product.id,
                obj.product.name,
                obj.product.category.name,
                obj.product.brand.name,
                obj.sale_price,
                obj.quantity,
                obj.subtotal,
                obj.sale_date.strftime("%Y-%m-%d %H:%M:%S"),
                obj.sale_invoice.user.username,
                "Evento" if obj.sale_invoice.sale_type == "EV" else "Venta",
                "SI" if obj.sale_invoice.voided else "NO",
            ]
        )
    return response


export_sale_item_as_csv.short_description = "Export selected to CSV"


@admin.register(SaleInvoiceItem)
class SaleInvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sale_invoice_id",
        "product",
        "sale_price",
        "quantity",
        "subtotal",
        "sale_date",
        "sale_invoice_user_username",
        "sale_invoice_sale_type",
        "sale_invoice_voided",
    )
    list_filter = (("sale_date", DateRangeFilter),)  # 👈 custom date range
    date_hierarchy = "sale_date"  # optional, for year/month/day navigation
    search_fields = ("product__name", "sale_invoice__id")
    actions = [export_sale_item_as_csv]

    def sale_invoice_sale_type(self, obj):
        return obj.sale_invoice.sale_type

    sale_invoice_sale_type.short_description = "Tipo de Venta"

    def sale_invoice_user_username(self, obj):
        return obj.sale_invoice.user.username

    sale_invoice_user_username.short_description = "Encargado de venta"

    def sale_invoice_voided(self, obj):
        return obj.sale_invoice.voided

    sale_invoice_voided.short_description = "Venta Padre Anulada"
    sale_invoice_voided.boolean = True


# region SaleInvoice admin
def export_sale_as_csv(modeladmin, request, queryset):
    """Export selected records to CSV"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="sale_invoices.csv"'
    writer = csv.writer(response)

    # Headers
    writer.writerow(
        [
            "ID Venta",
            "Cliente Nombres",
            "Cliente Apellidos",
            "Cliente NIT",
            "Total",
            "Fecha y hora de venta",
            "Tipo de Venta",
            "Anulado",
        ]
    )

    # Rows
    for obj in queryset.iterator():
        writer.writerow(
            [
                obj.id,
                obj.customer.first_name if obj.customer else "",
                obj.customer.last_name if obj.customer else "",
                obj.customer.nit if obj.customer else "C/F",
                obj.total,
                obj.sale_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Evento" if obj.sale_type == "EV" else "Venta",
                "SI" if obj.voided else "NO",
            ]
        )
    return response


export_sale_as_csv.short_description = "Export selected to CSV"


@admin.register(SaleInvoice)
class SaleInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "customer",
        "total",
        "sale_date",
        "sale_type",
        "voided",
    )
    list_filter = (
        ("sale_date", DateRangeFilter),
        "user",
        "sale_type",
        "voided",
    )  # 👈 custom date range
    date_hierarchy = "sale_date"  # optional, for year/month/day navigation
    search_fields = (
        "user__username",
        "customer__first_name",
        "customer__last_name",
        "customer__nit",
    )
    actions = [export_sale_as_csv]


#region CashFlow admin
def export_cash_flow_as_csv(modeladmin, request, queryset):
    """Export selected records to CSV"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="cash_flows.csv"'
    writer = csv.writer(response)

    # Headers
    writer.writerow(
        [
            "ID",
            "Creado por",
            "Descipcion",
            "Monto",
            "Tipo de transaccion",
            "Fecha de transaccion",
        ]
    )

    # Rows
    for obj in queryset.iterator():
        writer.writerow(
            [
                obj.id,
                obj.performed_by.username,
                obj.description,
                obj.amount,
                obj.operation_type,
                obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )
    return response


export_cash_flow_as_csv.short_description = "Export selected to CSV"


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = (
        "performed_by",
        "description",
        "amount",
        "operation_type",
        "created_at",
    )
    list_filter = (
        ("created_at", DateRangeFilter),
        "operation_type",
        "performed_by__username",
    )  # 👈 custom date range
    date_hierarchy = "created_at"  # optional, for year/month/day navigation
    search_fields = ("description", "performed_by__username")
    actions = [export_cash_flow_as_csv]
