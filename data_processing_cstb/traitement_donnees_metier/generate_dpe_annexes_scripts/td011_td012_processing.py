import pandas as pd
import numpy as np
from .utils import concat_string_cols, strip_accents, affect_lib_by_matching_score, clean_str, agg_pond_top_freq
from .trtvtables import DPETrTvTables

td011_types = {'td011_installation_chauffage_id': 'str',
               'td006_batiment_id': 'str',
               'tr003_type_installation_ch_id': 'category',
               'surface_chauffee': 'float',
               'nombre_appartements_echantillon': 'float',
               'surface_habitable_echantillon': 'float',
               'tv025_intermittence_id': 'category',
               }

td012_types = {'_td012_generateur_chauffage_id': 'str',
               'systeme_ch_cogeneration_id': 'string',
               'td011_installation_chauffage_id': 'str',
               'tr004_type_energie_id': 'category',
               'tv045_conversion_kwh_co2_id': 'category',
               'tv046_evaluation_contenu_co2_reseaux_id': 'category',
               'rendement_emission_systeme_ch': 'float',
               'tv028_rendement_emission_systeme_ch_id': 'category',
               'rendement_distribution_systeme_ch': 'str',
               'tv029_rendement_distribution_systeme_ch_id': 'category',
               'tv030_rendement_regulation_systeme_ch_id': 'category',
               'rendement_generation': 'float',
               'tv031_rendement_generation_id': 'category',
               'presence_regulation': 'int',
               'coefficient_performance': 'float',
               'tv032_coefficient_performance_id': 'category',
               'tv033_coefficient_correction_regulation_id': 'category',
               'tv034_temperature_fonctionnement_chaudiere_100_id': 'category',
               'tv035_temperature_fonctionnement_chaudiere_30_id': 'category',
               'rpn': 'float',
               'rpint': 'float',
               'qp0': 'float',
               'puissance_veilleuse': 'float',
               'tv036_puissance_veilleuse_id': 'category',
               'puissance_nominale': 'float',
               'tv038_puissance_nominale_id': 'category',
               'consommation_ch': 'float'}

replace_elec_tv045_ener = {"Electricité (hors électricité d'origine renouvelab": 'Electricité non renouvelable',
                           "Electricité d'origine renouvelable utilisée dans l": "Electricité d'origine renouvelable", }

# ===================== DICTIONARIES OF NORMALIZATION AND SIMPLIFICATION OF FIELDS ====================================

# dictionaries used to normalized chauffage names with simple labels.
gen_ch_lib_simp_dict = {
                        'convecteurs electriques nfc': 'generateurs a effet joule',
                        'panneaux rayonnants electriques nfc': 'generateurs a effet joule',
                        'radiateurs electriques': 'generateurs a effet joule',
                        'reseau de chaleur': 'reseau de chaleur',
                        'autres emetteurs a effet joule': 'generateurs a effet joule',
                        'plafonds/planchers rayonnants electriques nfc': 'generateurs a effet joule',
                        'chaudiere electrique': 'chaudiere electrique',
                        'poele ou insert fioul/gpl': 'poele ou insert fioul/gpl',
                        'convecteurs bi-jonction': 'generateurs a effet joule', }

# GEN CH NORMALIZED DICT
gen_ch_normalized_lib_matching_dict = {"pac air/air": ['pac', 'air/air', ('electricite', 'electrique')],
                                       "pac air/eau": ['pac', 'air/eau', ('electricite', 'electrique')],
                                       "pac eau/eau": ['pac', 'eau/eau', ('electricite', 'electrique')],
                                       "pac geothermique": ['pac', (
                                           'geothermique', 'geothermie'),
                                                            ('electricite', 'electrique')],
                                       'panneaux rayonnants electriques nfc': ['panneau', ('electricite', 'electrique'),
                                                                               'nfc'],
                                       'radiateurs electriques': ['radiateur', ('electricite', 'electrique')],
                                       'plafonds/planchers rayonnants electriques nfc': [('plancher', 'plafond'),
                                                                                         ('electricite', 'electrique')],
                                       "convecteurs electriques nfc": ['convecteur', ('electricite', 'electrique'),
                                                                       'nfc'],
                                       "poele ou insert bois": [('poele', 'insert'), ('bois', 'biomasse')],
                                       "poele ou insert fioul/gpl": [('poele', 'insert'), ('fioul', 'gpl')],
                                       "chaudiere bois": ['chaudiere',('bois','biomasse')],
                                       "autres emetteurs a effet joule": [('electricite', 'electrique')],
                                       "reseau de chaleur": ['reseau', 'chaleur'],
                                       "convecteurs bi-jonction": ['bi', 'jonction', ('electricite', 'electrique')],
                                       }

for type_chaudiere, type_chaudiere_keys in zip(['standard', 'basse temperature', 'condensation', 'indetermine'],
                                               [('standard', 'classique'), 'basse temperature',
                                                ('condensation', 'condenseurs'), None]):
    for energie in ['fioul', 'gaz','autre(gpl/butane/propane)']:
        energie_keywords = energie
        if energie == 'autre(gpl/butane/propane)':
            energie_keywords = ('gpl', 'butane', 'propane')
        if type_chaudiere_keys is not None:
            gen_ch_normalized_lib_matching_dict[f'chaudiere {energie} {type_chaudiere}'] = ['chaudiere', energie_keywords,
                                                                                            type_chaudiere_keys]
        else:
            gen_ch_normalized_lib_matching_dict[f'chaudiere {energie} {type_chaudiere}'] = ['chaudiere', energie_keywords
                                                                                            ]

gen_ch_normalized_lib_matching_dict['chaudiere bois/biomasse'] = ['chaudiere',
                                                                  ('bois', 'biomasse')]
gen_ch_normalized_lib_matching_dict['chaudiere electrique'] = ['chaudiere',
                                                               ('electricite', 'electrique')]
pac_dict = {2.2: 'pac air/air',
            2.6: 'pac air/eau',
            3.2: "pac eau/eau",
            4.0: "pac geothermique"}

poele_dict = {0.78: 'poele ou insert bois',
              0.66: 'poele ou insert bois',
              0.72: "poele ou insert fioul/gpl"}


def merge_td011_tr_tv(td011):
    meta = DPETrTvTables()
    table = td011.copy()
    table = meta.merge_all_tr_tables(table)
    table = meta.merge_all_tv_tables(table)
    table = table.astype(td011_types)
    table = table.rename(columns={'id': 'td007_paroi_opaque_id'})

    return table


def merge_td012_tr_tv(td012):
    meta = DPETrTvTables()
    table = td012.copy()
    table = meta.merge_all_tr_tables(table)
    table = meta.merge_all_tv_tables(table)
    table = table.astype({k: v for k, v in td012_types.items() if k in table})
    table = table.rename(columns={'id': 'td012_gen_ch_id'})

    return table


def postprocessing_td012(td012):
    table = td012.copy()

    is_rpn = table.rpn > 0
    is_rpint = table.rpint > 0
    is_chaudiere = is_rpint | is_rpn
    is_chaudiere = is_chaudiere | ~table.tv038_puissance_nominale_id.isnull()
    # all text description raw concat
    gen_ch_concat_txt_desc = table['tv031_type_generateur'].astype('string').replace(np.nan, '') + ' '
    gen_ch_concat_txt_desc.loc[is_chaudiere] += 'chaudiere '
    gen_ch_concat_txt_desc += table['tv036_type_chaudiere'].astype('string').replace(np.nan, ' ') + ' '
    gen_ch_concat_txt_desc += table["tv030_type_installation"].astype('string').replace(np.nan, ' ') + ' '
    gen_ch_concat_txt_desc += table["tv032_type_generateur"].astype('string').replace(np.nan, ' ') + ' '
    gen_ch_concat_txt_desc += table['tv035_type_chaudiere'].astype('string').replace(np.nan, ' ') + ' '
    gen_ch_concat_txt_desc += table['tv036_type_generation'].astype('string').replace(np.nan, ' ') + ' '
    gen_ch_concat_txt_desc += table["tv030_type_installation"].astype('string').replace(np.nan, ' ') + ' '
    gen_ch_concat_txt_desc += table["tr004_description"].astype('string').replace(np.nan, ' ') + ' '
    gen_ch_concat_txt_desc += table["tv045_energie"].astype('string').replace(np.nan, ' ') + ' '
    gen_ch_concat_txt_desc += table['tv046_nom_reseau'].isnull().replace({False: 'réseau de chaleur',
                                                                          True: ""})
    gen_ch_concat_txt_desc = gen_ch_concat_txt_desc.str.lower().apply(lambda x: strip_accents(x))

    table['gen_ch_concat_txt_desc'] = gen_ch_concat_txt_desc

    table['gen_ch_concat_txt_desc'] = table['gen_ch_concat_txt_desc'].apply(lambda x: clean_str(x))

    # calcul gen_ch_lib_infer par matching score text.
    unique_gen_ch = table.gen_ch_concat_txt_desc.unique()
    gen_ch_lib_infer_dict = {k: affect_lib_by_matching_score(k, gen_ch_normalized_lib_matching_dict) for k in
                             unique_gen_ch}
    table['gen_ch_lib_infer'] = table.gen_ch_concat_txt_desc.replace(gen_ch_lib_infer_dict)

    # calcul type energie chauffage

    table['type_energie_ch'] = table['tv045_energie'].replace(replace_elec_tv045_ener)

    # recup/fix PAC
    is_pac = (table.coefficient_performance > 2) | (table.rendement_generation > 2)
    table.loc[is_pac, 'gen_ch_lib_infer'] = table.loc[is_pac, 'coefficient_performance'].replace(pac_dict)
    is_ind = is_pac & (~table.loc[is_pac, 'gen_ch_lib_infer'].isin(pac_dict.values()))
    table.loc[is_ind, 'gen_ch_lib_infer'] = table.loc[is_ind, 'rendement_generation'].replace(pac_dict)
    is_ind = is_pac & (~table.loc[is_pac, 'gen_ch_lib_infer'].isin(pac_dict.values()))
    table.loc[is_ind, 'gen_ch_lib_infer'] = 'pac indetermine'

    # recup/fix poele bois
    is_bois = table.gen_ch_concat_txt_desc == 'bois, biomasse bois, biomasse'

    table.loc[is_bois, 'gen_ch_lib_infer'] = table.loc[is_bois, 'rendement_generation'].replace(poele_dict)

    is_ind = is_bois & (~table.loc[is_bois, 'gen_ch_lib_infer'].isin(poele_dict.values()))
    table.loc[is_ind, 'gen_ch_lib_infer'] = 'indetermine'

    # recup reseau chaleur
    non_aff = table.gen_ch_lib_infer == 'indetermine'

    reseau_infer = non_aff & (table.rendement_generation == 0.97) & (table.tr004_description == 'Autres énergies')

    table.loc[reseau_infer, 'gen_ch_lib_infer'] = 'reseau de chaleur'
    table.loc[reseau_infer, 'type_energie_ch'] = 'Réseau de chaleurs'

    table['gen_ch_lib_infer_simp'] = table.gen_ch_lib_infer.replace(gen_ch_lib_simp_dict)

    # fix chaudiere elec

    bool_ej = table.gen_ch_lib_infer == 'autres emetteurs a effet joule'
    bool_ce = table.rendement_generation == 0.77

    table.loc[(bool_ej) & (bool_ce), 'gen_ch_lib_infer'] = 'chaudiere electrique'

    rendement_gen_u = table[['rendement_generation', 'coefficient_performance']].max(axis=1)

    s_rendement = pd.Series(index=table.index)
    s_rendement[:] = 1
    for rendement in ['rendement_distribution_systeme_ch',
                      'rendement_emission_systeme_ch']:
        r = table[rendement].astype(float)
        r[r == 0] = 1
        r[r.isnull()] = 1
        s_rendement = s_rendement * r

    rendement_gen_u[rendement_gen_u == 0] = 1
    rendement_gen_u[rendement_gen_u.isnull()] = 1
    s_rendement = s_rendement * rendement_gen_u
    table['besoin_ch_infer'] = table['consommation_ch'] * s_rendement

    return table


def agg_systeme_ch_essential(td001, td011, td012):
    sys_ch_princ_rename = {
        'td001_dpe_id': 'td001_dpe_id',
        'gen_ch_lib_infer': 'sys_ch_princ_gen_ch_lib_infer',
        'gen_ch_lib_infer_simp': 'sys_ch_princ_gen_ch_lib_infer_simp',
        'type_energie_ch': 'sys_ch_princ_type_energie_ch',
        'consommation_ch': 'sys_ch_princ_conso_ch',
        "tv025_type_installation": 'sys_ch_princ_type_installation_ch',
        'nb_generateurs': 'sys_ch_princ_nb_generateur'
    }

    sys_ch_sec_rename = {
        'td001_dpe_id': 'td001_dpe_id',
        'gen_ch_lib_infer': 'sys_ch_sec_gen_ch_lib_infer',
        'gen_ch_lib_infer_simp': 'sys_ch_sec_gen_ch_lib_infer_simp',
        'type_energie_ch': 'sys_ch_sec_type_energie_ch',
        'consommation_ch': 'sys_ch_sec_conso_ch',
        "tv025_type_installation": 'sys_ch_sec_type_installation_ch',
        'nb_generateurs': 'sys_ch_sec_nb_generateur'
    }

    sys_ch_tert_concat_rename = {
        'td001_dpe_id': 'td001_dpe_id',
        'gen_ch_lib_infer': 'sys_ch_tert_gen_ch_lib_infer_concat',
        'gen_ch_lib_infer_simp': 'sys_ch_tert_gen_ch_lib_infer_simp_concat',
        'type_energie_ch': 'sys_ch_tert_type_energie_ch_concat',
        'consommation_ch': 'sys_ch_tert_conso_ch',
        "tv025_type_installation": 'sys_ch_tert_type_installation_ch_concat',
        'nb_generateurs': 'sys_ch_tert_nb_generateurs'
    }

    td012 = td012.merge(
        td011[['td011_installation_chauffage_id', 'tv025_intermittence_id', "tv025_type_installation"]],
        on='td011_installation_chauffage_id', how='left')
    table = td012
    rendement_gen_u = table[['rendement_generation', 'coefficient_performance']].max(axis=1)

    s_rendement = pd.Series(index=table.index)
    s_rendement[:] = 1
    for rendement in ['rendement_distribution_systeme_ch',
                      'rendement_emission_systeme_ch']:
        r = table[rendement].astype(float)
        r[r == 0] = 1
        r[r.isnull()] = 1
        s_rendement = s_rendement * r

    rendement_gen_u[rendement_gen_u == 0] = 1
    rendement_gen_u[rendement_gen_u.isnull()] = 1
    s_rendement = s_rendement * rendement_gen_u
    table['besoin_ch_infer'] = table['consommation_ch'] * s_rendement

    table['nb_generateurs'] = 1

    cols = ['td001_dpe_id', 'gen_ch_lib_infer_simp', 'gen_ch_lib_infer', 'type_energie_ch',
            'consommation_ch', 'besoin_ch_infer']
    cols += ['tv025_intermittence_id', "tv025_type_installation", 'nb_generateurs', 'id_unique']

    agg_cols = ['td001_dpe_id', 'gen_ch_lib_infer', 'tv025_intermittence_id']

    table['id_unique'] = table.td001_dpe_id + table.gen_ch_lib_infer + table.tv025_intermittence_id.astype(str)

    is_unique = table.groupby('td001_dpe_id').td001_dpe_id.count() == 1
    ist_unique = is_unique[is_unique].index

    table_gen_unique = table.loc[table.td001_dpe_id.isin(ist_unique)][cols]

    table_gen_multiple = table.loc[~table.td001_dpe_id.isin(ist_unique)][cols]

    table_gen_multiple[agg_cols] = table_gen_multiple[agg_cols].astype(str)

    agg = table_gen_multiple.groupby(agg_cols).agg({
        'gen_ch_lib_infer_simp': 'first',
        'type_energie_ch': 'first',
        'consommation_ch': 'sum',
        'besoin_ch_infer': 'sum',
        "tv025_type_installation": 'first',
        "nb_generateurs": 'sum'

    }).reset_index()

    agg['id_unique'] = agg.td001_dpe_id + agg.gen_ch_lib_infer + agg.tv025_intermittence_id

    sys_princ = agg.sort_values('consommation_ch', ascending=False).drop_duplicates(subset='td001_dpe_id')

    id_sys_princ = sys_princ.id_unique.unique().tolist()

    sys_secs = agg.loc[~agg.id_unique.isin(id_sys_princ)]

    sys_sec = sys_secs.sort_values('consommation_ch', ascending=False).drop_duplicates(
        'td001_dpe_id')

    id_sys_sec = sys_sec.id_unique.unique().tolist()

    sys_terts = agg.loc[~agg.id_unique.isin(id_sys_princ + id_sys_sec)]

    sys_tert_concat = sys_terts.groupby('td001_dpe_id').agg({
        'gen_ch_lib_infer': lambda x: ' + '.join(sorted(list(set(x)))),

        'gen_ch_lib_infer_simp': lambda x: ' + '.join(sorted(list(set(x)))),
        'type_energie_ch': lambda x: ' + '.join(sorted(list(set(x)))),
        'consommation_ch': 'sum',
        'besoin_ch_infer': 'sum',
        "tv025_type_installation": lambda x: ' + '.join(sorted(list(set(x)))),
        'nb_generateurs': 'sum'
    }).reset_index()

    sys_princ = sys_princ.append(table_gen_unique[sys_princ.columns])

    sys_princ = sys_princ.rename(columns=sys_ch_princ_rename)[sys_ch_princ_rename.values()]

    sys_sec = sys_sec.rename(columns=sys_ch_sec_rename)[sys_ch_sec_rename.values()]

    sys_tert_concat = sys_tert_concat.rename(columns=sys_ch_tert_concat_rename)[
        sys_ch_tert_concat_rename.values()]

    td001_sys_ch = td001[['td001_dpe_id']].merge(sys_princ, on='td001_dpe_id', how='left')
    td001_sys_ch = td001_sys_ch.merge(sys_sec, on='td001_dpe_id', how='left')
    td001_sys_ch = td001_sys_ch.merge(sys_tert_concat, on='td001_dpe_id', how='left')
    nb_installation = td011.groupby('td001_dpe_id').td011_installation_chauffage_id.count().to_frame(
        'nb_installations_ch_total')
    td001_sys_ch = td001_sys_ch.merge(nb_installation, on='td001_dpe_id', how='left')

    cols_end = sys_princ.columns.tolist() + sys_sec.columns.tolist() + sys_tert_concat.columns.tolist()
    cols_end = np.unique(cols_end).tolist()
    cols_end.remove('td001_dpe_id')

    td001_sys_ch['nb_gen_ch_total'] = td001_sys_ch.sys_ch_princ_nb_generateur
    td001_sys_ch['nb_gen_ch_total'] += td001_sys_ch.sys_ch_sec_nb_generateur.fillna(0)
    td001_sys_ch['nb_gen_ch_total'] += td001_sys_ch.sys_ch_tert_nb_generateurs.fillna(0)

    cols = ['sys_ch_princ_type_energie_ch',
            'sys_ch_sec_type_energie_ch',
            'sys_ch_tert_type_energie_ch_concat']

    td001_sys_ch['mix_energetique_ch'] = concat_string_cols(td001_sys_ch, cols=cols, join_string=' + ',
                                                                   is_unique=True, is_sorted=True)

    cols = ['sys_ch_princ_type_installation_ch',
            'sys_ch_sec_type_installation_ch',
            'sys_ch_tert_type_installation_ch_concat']

    td001_sys_ch['type_installation_ch_concat'] = concat_string_cols(td001_sys_ch, cols=cols, join_string=' + ',
                                                                            is_unique=True, is_sorted=True)

    cols = ['sys_ch_princ_gen_ch_lib_infer',
            'sys_ch_sec_gen_ch_lib_infer',
            'sys_ch_tert_gen_ch_lib_infer_concat']

    td001_sys_ch['gen_ch_lib_infer_concat'] = concat_string_cols(td001_sys_ch, cols=cols, join_string=' + ',
                                                                 is_unique=True, is_sorted=True)

    cols = ['sys_ch_princ_gen_ch_lib_infer_simp',
            'sys_ch_sec_gen_ch_lib_infer_simp',
            'sys_ch_tert_gen_ch_lib_infer_simp_concat']

    td001_sys_ch['gen_ch_lib_infer_simp_concat'] = concat_string_cols(td001_sys_ch, cols=cols, join_string=' + ',
                                                                      is_unique=True, is_sorted=True)

    cfg_installation_ch = td011.groupby('td001_dpe_id').tr003_description.apply(
        lambda x: ' + '.join(sorted(list(set(x))))).to_frame('cfg_installation_ch')
    # isnull = td001_sys_ch.sys_ch_princ_nb_generateur.isnull()
    # is_multiple_install = td001_sys_ch.nb_installations_ch_total > 1
    # td001_sys_ch.loc[isnull, 'cfg_sys_ch'] = pd.NA
    # td001_sys_ch.loc[~isnull, 'cfg_sys_ch'] = 'type de générateur unique/installation unique'
    # isnull = td001_sys_ch.sys_ch_sec_nb_generateur.isnull()
    # td001_sys_ch.loc[~isnull, 'cfg_sys_ch'] = 'types de générateur multiples/installation unique'
    # td001_sys_ch.loc[(~isnull) & (
    #     is_multiple_install), 'cfg_sys_ch'] = 'types de générateur multiples/installations multiples'
    td001_sys_ch = td001_sys_ch.merge(cfg_installation_ch.reset_index(), on='td001_dpe_id')
    cols_first = [el for el in td001_sys_ch.columns.tolist() if el not in cols_end]

    cols = cols_first + cols_end

    return td001_sys_ch[cols]
