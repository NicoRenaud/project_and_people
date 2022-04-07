# -*- mode: python ; coding: utf-8 -*-
# This is a specification file for compiling the application into a single folder

block_cipher = None


a = Analysis(['server.py'],
             pathex=['C:\\Users\\NicolasRenaud\\project_and_people'],
             binaries=[],
             datas=[
                  ('C:/Users/NicolasRenaud/Anaconda3/envs/or_tools/lib/site-packages/dash_core_components','dash_core_components'),
                  ('C:/Users/NicolasRenaud/Anaconda3/envs/or_tools/lib/site-packages/dash_html_components',
                  'dash_html_components'),
                  ('C:/Users/NicolasRenaud/Anaconda3/envs/or_tools/lib/site-packages/dash_bootstrap_components','dash_bootstrap_components'),
                  ('C:/Users/NicolasRenaud/Anaconda3/envs/or_tools/lib/site-packages/plotly',
                  'plotly'),
                  ('C:/Users/NicolasRenaud/Anaconda3/envs/or_tools/lib/site-packages/dash_renderer',
                  'dash_renderer'),
                  ('C:/Users/NicolasRenaud/Anaconda3/envs/or_tools/lib/site-packages/dash',
                  'dash'),
                  ('C:/Users/NicolasRenaud/project_and_people/assets','assets'),
                  ('C:/Users/NicolasRenaud/project_and_people/data','data'),
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
          [],
          exclude_binaries=True,
          name='launch_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          icon = 'assets/icon.ico',
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='app')
