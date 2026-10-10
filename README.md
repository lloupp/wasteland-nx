# Wasteland NX — Fallout: New Vegas for Nintendo Switch

Projeto de pesquisa **não oficial**, focado exclusivamente em **Fallout: New Vegas**, com suporte a arquivos de uma instalação legítima da **Epic Games**.

**Estado atual:** preflight de arquivos no PC e ferramentas experimentais de exploração de ESM/BSA. **Não existe port jogável ou `.nro` validado no Switch.** O executável original x86 não funciona diretamente no processador ARM do console.

## Preparar sua instalação Epic (Windows)

1. Instale Python 3.
2. Baixe este repositório (Code → Download ZIP) e extraia.
3. Execute `INICIAR_EPIC_WINDOWS.cmd`.
4. Se a detecção falhar, use `INICIAR_EPIC_WINDOWS.cmd --data "D:\\Epic Games\\FalloutNewVegas"`, alterando o diretório.
5. Compartilhe apenas `newvegas-relatorio.json`. Não compartilhe os arquivos comerciais.

O programa só lê manifestos e cabeçalhos locais, não modifica o jogo nem envia dados pela internet. O relatório não deve incluir caminhos absolutos.

## Roteiro de engenharia

1. Validar preflight Epic e leitura de ESM/BSA com arquivos reais.
2. Ler modelos NIF/texturas DDS no PC; visualizar uma célula de Goodsprings.
3. Construir renderizador e controles nativos do Switch (devkitPro/deko3d).
4. Implementar colisões, interação, scripts, diálogos, NPCs, missões, combate e saves.

Os arquivos do jogo, recursos artísticos e binários proprietários não podem ser incluídos no repositório. Código original de ferramentas: MIT.

> A versão experimental 0.4 existente em ZIP contém componentes C++ e um visualizador de pontos; a sincronização desses componentes com este repositório ainda não foi concluída.
