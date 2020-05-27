td007_types = {'id': 'str',
               'td006_batiment_id': 'str',
               'tr014_type_parois_opaque_id': 'category',
               'reference': 'category',
               'deperdition_thermique': 'float',
               'tv001_coefficient_reduction_deperditions_id': 'category',
               'tv002_local_non_chauffe_id': 'category',
               'coefficient_transmission_thermique_paroi': 'float',
               'coefficient_transmission_thermique_paroi_non_isolee': 'float',
               'tv003_umur_id': 'category',
               'tv004_umur0_id': 'category',
               'tv005_upb_id': 'category',
               'tv006_upb0_id': 'category',
               'tv007_uph_id': 'category',
               'tv008_uph0_id': 'category',
               'resistance_thermique_isolation': 'float',
               'epaisseur_isolation': 'float',
               'surface_paroi': 'float',
               'tr014_Sous-Type': 'category',
               'tr014_Est_efface': 'category',
               'tv001_aiu_aue': 'category',
               'tv001_aiu_aue_min': 'category',
               'tv001_aiu_aue_max': 'category',
               'tv001_uv_ue': 'category',
               'tv001_aue_isole': 'category',
               'tv001_aiu_isole': 'category',
               'tv001_valeur': 'category',
               'tv001_est_efface': 'category',
               'tv002_Type de Bâtiment': 'category',
               'tv002_Local non chauffée': 'category',
               'tv002_Uv,ue': 'category',
               'tv003_Mur Isolé': 'category',
               'tv003_Année construction': 'category',
               'tv003_Année isolation': 'category',
               'tv003_Zone Hiver': 'category',
               'tv003_Effet Joule': 'category',
               'tv003_Umur': 'category',
               'tv004_Matériaux': 'category',
               'tv004_épaisseur': 'category',
               'tv004_Umur0': 'category',
               'tv005_Pb Isolé': 'category',
               'tv005_2S/P': 'category',
               'tv005_Année construction': 'category',
               'tv005_Année isolation': 'category',
               'tv005_Zone Hiver': 'category',
               'tv005_Effet Joule': 'category',
               'tv005_Upb': 'category',
               'tv006_Matériaux': 'category',
               'tv006_Upb0': 'category',
               'tv007_Ph Isolé': 'category',
               'tv007_Type  de Toit': 'category',
               'tv007_Année construction': 'category',
               'tv007_Année isolation': 'category',
               'tv007_Zone Hiver': 'category',
               'tv007_Effet Joule': 'category',
               'tv007_Uph': 'category',
               'tv008_Matériaux': 'category',
               'tv008_Uph0': 'category'}


def merge_td007_tr_tv(td007):
    from assets_orm import DPEMetaData
    meta = DPEMetaData()
    table = td007.copy()
    table = meta.merge_all_tr_table(table)

    table = meta.merge_all_tv_table(table)

    return table


def postprocessing_td007(td007):
    table = td007.copy()
    table = table.astype(td007_types)
    return table
