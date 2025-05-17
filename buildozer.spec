[app]

# Título e nome do pacote
title = Test
package.name = testapp
package.domain = org.test

# Versão
version = 1.0

# Código fonte
source.dir = .
source.include_exts = py
source.exclude_dirs = bin, build, dist, __pycache__, venv

# Requisitos - simplificando para resolver problemas de dependência
requirements = python3,kivy

# Orientação
orientation = portrait

# Configurações do Android
android.archs = arm64-v8a
android.api = 28
android.minapi = 21
android.ndk = 25c

# Bootstrap
p4a.bootstrap = sdl2
p4a.port = 8000

# Compilação
log_level = 2

[buildozer]
log_level = 2 