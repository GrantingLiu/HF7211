# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis([
'demo.py',
'Ui_pw1dialog.py',
'Ui_control.py',
'transfer.py',
'signalslot.py',
'image_rc.py'],
             pathex=['E:\\Work\\HF7211_Soft_100J_WIFI'],
             binaries=[],
             datas=[('E:\\Work\\HF7211_Soft_100J_WIFI\\res','res'),('E:\\Work\\HF7211_Soft_100J_WIFI\\log_machine','log_machine'),('E:\\Work\\HF7211_Soft_100J_WIFI\\log_comm','log_comm'),('E:\\Work\\HF7211_Soft_100J_WIFI\\log_user','log_user')],
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
          name='Control',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='demo')
