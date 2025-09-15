# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['VirPhyKit.py'],
    pathex=[],
    binaries=[],
    datas=[('MOT/Insert_node_numbers.py', 'scripts'), ('MOT/AfterPhylo.pl', 'scripts'), ('MOT/Get_migration_matrix_general_number_of_categories.py', 'scripts'), ('MOT/process_tree.R', 'scripts'), ('MOTP/plot_migration_over_time.R', 'scripts'), ('MOTP/plot_migration_over_time_smooth.R', 'scripts'), ('Group/Mapping.txt', 'scripts'), ('Group/Mapping.txt', '.'), ('SamplePlot/generate_plot.R', 'scripts'), ('SamplePlot/generate_map.R', 'scripts'), ('Treedater/treedater.R', 'scripts'), ('icon.ico', '.'), ('About/icon.ico', 'About'), ('Treetime/Mapping.txt', '.'), ('Quick_Guide.pdf', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VirPhyKit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
