from farol.rotulos import rotulo, slug, federal, ano_do_id


def test_rotulos_basicos():
    assert rotulo("UFPB-CONSEPE-RES-29-2020") == "Res. CONSEPE 29/2020"
    assert rotulo("BR-LEI-9394-1996") == "Lei 9.394/1996"
    assert rotulo("BR-DEC-9235-2017") == "Decreto 9.235/2017"
    assert rotulo("BR-CNE-CES-RES-2-2019") == "Res. CNE/CES 2/2019"
    assert rotulo("BR-MEC-PORT-3198-2002") == "Portaria MEC 3.198/2002"
    assert rotulo("BR-IN-SLTI-4-2010") == "IN SLTI 4/2010"
    assert rotulo("BR-?-PORT-1-2024", orgao="?") == "Portaria ? 1/2024"


def test_rotulos_fixos():
    assert rotulo("UFPB-REGIMENTO-GERAL") == "Regimento Geral da UFPB"
    assert rotulo("UFPB-CONSUNI-RES-07-2002").startswith("Estatuto da UFPB")


def test_slug_e_federal():
    assert slug("BR-?-RES-1-2020") == "BR-_-RES-1-2020"
    assert federal("BR-LEI-8112-1990") and not federal("UFPB-CONSUNI-RES-07-2002")
    assert ano_do_id("UFPB-CONSEPE-RES-16-2015") == "2015"
