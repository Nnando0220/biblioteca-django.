# Sistema de Gerenciamento de Biblioteca

Este projeto é um sistema de gerenciamento de biblioteca, onde é possível cadastrar, visualizar, atualizar e deletar livros, autores e categorias. O sistema foi desenvolvido com Django, utilizando o ORM para operações CRUD e serializers manuais para manipulação de dados. As views são baseadas em função (Function-Based Views - FBVs) e expõem uma API RESTful.

## Funcionalidades

- **CRUD de Livros, Autores e Categorias**: Permite criar, listar, editar e excluir registros.
- **API RESTful**: Implementação de uma API para gerenciar os dados da biblioteca.
- **HyperlinkedModelSerializer**: Serialização de objetos usando a classe `HyperlinkedModelSerializer` do Django Rest Framework.
- **Django ORM**: Operações de consulta, inserção, atualização e exclusão de dados no banco.
- **Interface com Banco de Dados SQLite**: Utiliza SQLite como banco de dados padrão.

## Tecnologias Utilizadas

- **Django**: Framework para desenvolvimento web.
- **Django ORM**: Gerenciamento de banco de dados através do ORM do Django.
- **Django Rest Framework**: Para a criação da API RESTful.
- **SQLite**: Banco de dados utilizado neste projeto.
- **Python**: Linguagem de programação.
