"""
RTL helpers for Arabic UI text in CustomTkinter/Tkinter.

Tk on Windows often draws Arabic mixed with Latin words in the wrong visual order,
especially inside labels and buttons.  We reshape Arabic letters and apply the
Unicode bidi algorithm only for STATIC UI text.  User-entered values and document
contents are kept raw so they can be saved correctly in the database and Word files.
"""

import re

_ARABIC_RE = re.compile(r"[\u0600-\u06FF]")

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except Exception:  # The app can still run if the packages are missing.
    arabic_reshaper = None
    get_display = None


def has_arabic(value) -> bool:
    return isinstance(value, str) and bool(_ARABIC_RE.search(value))


def rtl_text(value):
    """Return a display-safe version of Arabic static text."""
    if not has_arabic(value):
        return value
    if arabic_reshaper is None or get_display is None:
        return value
    try:
        reshaped = arabic_reshaper.reshape(value)
        return get_display(reshaped)
    except Exception:
        return value


def apply_rtl_patches(ctk):
    """Patch common CustomTkinter widgets so Arabic UI strings display correctly."""

    def patch_widget_class(class_name, convert_keys, defaults=None):
        cls = getattr(ctk, class_name, None)
        if cls is None or getattr(cls, "_idara_rtl_patched", False):
            return

        original_init = cls.__init__
        original_configure = cls.configure

        def convert_kwargs(kwargs):
            for key in convert_keys:
                if key in kwargs and isinstance(kwargs[key], str):
                    kwargs[key] = rtl_text(kwargs[key])
            if defaults:
                for key, val in defaults.items():
                    kwargs.setdefault(key, val)
            return kwargs

        def __init__(self, *args, **kwargs):
            original_init(self, *args, **convert_kwargs(kwargs))

        def configure(self, *args, **kwargs):
            return original_configure(self, *args, **convert_kwargs(kwargs))

        cls.__init__ = __init__
        cls.configure = configure
        cls.config = configure
        cls._idara_rtl_patched = True

    # Static text widgets.
    patch_widget_class("CTkLabel", ["text"], {"anchor": "e", "justify": "right"})
    patch_widget_class("CTkButton", ["text"], {"anchor": "center"})
    patch_widget_class("CTkCheckBox", ["text"], {"anchor": "e"})
    patch_widget_class("CTkRadioButton", ["text"], {"anchor": "e"})

    # Input placeholders only; actual user input remains unchanged.
    patch_widget_class("CTkEntry", ["placeholder_text"], {"justify": "right"})
    patch_widget_class("CTkComboBox", ["button_hover_color"], {})


__all__ = ["rtl_text", "apply_rtl_patches", "has_arabic"]
