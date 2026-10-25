"""Filtros de presentación para las plantillas del catálogo.

Solo separan textos ya guardados para mostrarlos en listas; no calculan
reglas del dominio ni cambian los datos.
"""
from django import template

register = template.Library()


@register.filter
def lineas(texto):
    """Cada línea no vacía de un texto, sin espacios sobrantes."""
    return [linea.strip() for linea in (texto or "").splitlines() if linea.strip()]


@register.filter
def elementos(texto):
    """Elementos de una lista escrita como «a; b; c.»."""
    return [parte.strip().rstrip(".").strip() for parte in (texto or "").split(";") if parte.strip(" .")]


@register.filter
def licencia(texto):
    """Separa «CC BY-SA 4.0 — https://...» en nombre y enlace."""
    nombre, _, resto = (texto or "").partition(" — ")
    url = resto.split()[0] if resto.startswith("http") else ""
    extra = resto[len(url):].strip(" .") if url else resto.strip()
    return {"nombre": nombre.strip(), "url": url, "extra": extra}
