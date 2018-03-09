#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pks import PubKeySync

if __name__ == "__main__":
    pks_obj = PubKeySync()
    pks_obj.printlog('Pushing public keys to remote servers...')
    pks_obj.push_keys(True)