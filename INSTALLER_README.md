# IDARA DZ Installer Build

تم تحويل المشروع إلى نسخة تثبيت احترافية.

## الملفات المضافة/المعدلة

```text
.github/workflows/build.yml
installer/IDARA_DZ.iss
utils/paths.py
```

## النتيجة بعد GitHub Actions

سيظهر Artifact باسم:

```text
IDARA_DZ_Setup
```

داخله:

```text
IDARA_DZ_Setup_v1.1.exe
```

## لماذا هذا أفضل؟

- البرنامج يثبت على الحاسوب.
- يظهر في Start Menu.
- يمكن إنشاء اختصار على سطح المكتب.
- يظهر في Programs and Features لإزالته.
- التشغيل أسرع لأن البناء أصبح `--onedir` بدل `--onefile`.
- بيانات المستخدم تحفظ في:

```text
%LOCALAPPDATA%\IDARA_DZ
```

وهذا يحمي قاعدة البيانات والوثائق والنسخ الاحتياطية عند تحديث البرنامج.

## ملاحظة

إذا أردت أيقونة رسمية لاحقًا، أرسل ملف `app_icon.ico` وسنفعله في ملف التثبيت والبناء.
