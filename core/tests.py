from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Colecao, Livro, Categoria, Autor
from django.core.cache import cache


class ColecaoTests(APITestCase):
    def create_user_and_set_token_credentials(self):
        user = User.objects.create_user(
            username="testuser",
            password="12345",
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return user

    def post_colecao(self, nome, descricao, livros=None):
        if livros is None:
            livros = []
        url = reverse("colecao-list")
        data = {
            "nome": nome,
            "descricao": descricao,
            "livros": livros,
            "colecionador": self.user.username
        }
        response = self.client.post(url, data, format="json")
        return response

    def setUp(self):
        self.user = self.create_user_and_set_token_credentials()
        self.categoria = Categoria.objects.create(nome="Ficção Científica")
        self.autor = Autor.objects.create(nome="Isaac Asimov")
        self.livro = Livro.objects.create(
            titulo="Eu, Robô",
            autor=self.autor,
            categoria=self.categoria,
            publicado_em="1950-12-02",
        )
        self.colecao = Colecao.objects.create(
            nome="Favoritos",
            descricao="Livros favoritos do usuário",
            colecionador=self.user,
        )
        self.colecao.livros.add(self.livro)

    # Testa a criação de uma nova coleção
    def test_post_and_get_colecao(self):
        new_colecao_nome = "Minha Coleção"
        response = self.post_colecao(new_colecao_nome, "Descrição da coleção", [])
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Colecao.objects.count(), 2)
        self.assertEqual(new_colecao_nome, Colecao.objects.last().nome)

    # Testa a criação de uma coleção sem autenticação
    def test_post_colecao_without_auth(self):
        self.client.credentials()  # Remove o token de autenticação
        response = self.post_colecao("Coleção Anônima", "Sem token", [])
        print(response.json())
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    # Testa a permissão para edição de uma coleção
    def test_edit_colecao_by_owner(self):
        url = reverse("colecao-detail", args=[self.colecao.id])
        updated_name = "Coleção Atualizada"
        data = {"nome": updated_name}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.colecao.refresh_from_db()
        self.assertEqual(self.colecao.nome, updated_name)

    def test_edit_colecao_by_non_owner(self):
        other_user = User.objects.create_user(
            username="otheruser", password="12345"
        )
        other_token = Token.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {other_token.key}")
        url = reverse("colecao-detail", args=[self.colecao.id])
        response = self.client.patch(url, {"nome": "Alteração Proibida"}, format="json")
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # Testa a exclusão de uma coleção pelo dono
    def test_delete_colecao_by_owner(self):
        url = reverse("colecao-detail", args=[self.colecao.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(Colecao.objects.count(), 0)

    # Testa a exclusão de uma coleção por outro usuário
    def test_delete_colecao_by_non_owner(self):
        other_user = User.objects.create_user(
            username="otheruser", password="12345"
        )
        other_token = Token.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {other_token.key}")
        url = reverse("colecao-detail", args=[self.colecao.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # Testa a listagem de coleções visíveis
    def test_list_colecoes(self):
        url = reverse("colecao-list")
        response = self.client.get(url, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nome"], self.colecao.nome)

    # Testa o filtro por nome de coleção
    def test_filter_colecao_by_nome(self):
        url = f"{reverse('colecao-list')}?nome={self.colecao.nome}"
        response = self.client.get(url, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nome"], self.colecao.nome)


class ColecaoPermissionsTests(APITestCase):
    def setUp(self):
        # Criando usuários e seus tokens
        self.user1 = User.objects.create_user("user01", "user01@example.com", "user01P4ssw0D")
        self.token1 = Token.objects.create(user=self.user1)

        self.user2 = User.objects.create_user("user02", "user02@example.com", "user02P4ssw0D")
        self.token2 = Token.objects.create(user=self.user2)

        # Autenticando inicialmente com user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')

        # Criando categoria e autor
        self.categoria = Categoria.objects.create(nome="Categoria Teste")
        self.autor = Autor.objects.create(nome="Autor Teste")

        # Criando o livro
        self.livro = Livro.objects.create(
            titulo="Livro Teste",
            autor=self.autor,
            categoria=self.categoria,
            publicado_em="2023-11-22"
        )

        # Criando uma coleção para o user1
        self.colecao = Colecao.objects.create(
            nome="Coleção do User1",
            descricao="Descrição da Coleção",
            colecionador=self.user1
        )

    def test_user_permissions_on_colecao(self):
        # Tentar editar a coleção como usuário não dono (user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        url = reverse("colecao-detail", kwargs={"pk": self.colecao.pk})
        response = self.client.patch(url, {"nome": "Novo nome"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Login do dono da coleção
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.patch(url, {"nome": "Novo nome"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ThrottlingTestColecao(APITestCase):
    def setUp(self):
        # Limpar cache antes de cada teste
        cache.clear()

        # Configurar usuário de teste
        self.user1 = User.objects.create_user("user01", "user01@example.com", "user01P4ssw0D")
        self.token1 = Token.objects.create(user=self.user1)

        # Configurar URL do endpoint
        self.colecao_url = reverse("colecao-list")

        # Criar coleções para teste
        for i in range(10):
            Colecao.objects.create(
                nome=f"Coleção {i}",
                descricao="Descrição",
                colecionador=self.user1
            )

    def tearDown(self):
        # Limpar cache após cada teste
        cache.clear()

    def test_colecao_throttle_limit(self):
        """Teste de throttling específico para coleções (200/hora)"""
        # Configurar autenticação
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')

        # Fazer requisições até o limite
        for _ in range(200):
            response = self.client.get(self.colecao_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 201ª requisição deve ser bloqueada
        response = self.client.get(self.colecao_url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
