#!/bin/bash
# Salir si hay algún error
set -e

echo "🔹 Instalando Poetry..."

# Descargar e instalar Poetry usando el script oficial
curl -sSL https://install.python-poetry.org | python3 -

# Agregar Poetry al PATH (necesario si no se carga automáticamente)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.bashrc || source ~/.zshrc

# Verificar instalación
echo "✅ Verificando instalación de Poetry..."
poetry --version

echo "🎉 Poetry instalado correctamente."
