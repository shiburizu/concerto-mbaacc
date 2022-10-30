# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
block_cipher = None

a = Analysis(['concerto.py','mbaacc.py','config.py'],
            binaries=[('winpty-agent.exe','winpty')],
            datas=[
                ('mbaacc.py','.'),
                ('config.py','.'),
                ('presence.py','.'),
                ('Concerto.kv','.'),
                ('./ui','/ui'),
                ('./res','/res')
            ],
            hiddenimports=[],
            hookspath=[],
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
            cipher=block_cipher)
exe = EXE(pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
            name='Concerto',
            debug=True,
            bootloader_ignore_signals=False,
            strip=False,
            upx=False,
            upx_exclude=[],
            runtime_tmpdir=None,
            console=False,
            icon='concertoicon.ico')