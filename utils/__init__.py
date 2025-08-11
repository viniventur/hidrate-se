from utils.config import (
    is_local,
    nome_pag_title,
    img_pag_icon,
    modulos,
    voltar_inicio,
    data_hr_atual,
    data_atual
)
from utils.conn_gdriver import (
    get_drive_service,
    list_login_files,
    download_file_from_drive_id,
    criar_pasta,
    upload_csv,
    download_file_by_name,
    df_usuarios_cpf,
    df_historico_acesso,
    df_orgaos_acesso,
    df_unidades_acesso,
    recarregar_usuarios,
    upload_and_replace_file_drive
)
from utils.conn_gsheets import (
    obter_dados_pessoal,
    obter_dados_acompanhamento,
    connect_to_gsheet,
    novo_registro,
    conferir_registro_duplicado,
    dados_nomes_select,
    dados_analise_meta,
    dados_analise_meta_diaria
)
from utils.validacao_dados import (
    get_image_as_base64,
    converter_para_excel,
    cont_dias,
    padronizar_data,
    ml_para_litros
)
from utils.analise_ranking import(
    analise_ranking
)