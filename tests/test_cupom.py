from app import db
from models import Produto
import json


def create_user(email='user@example.com', password='123', tipo='administrador'):
    from models import Usuario
    user = Usuario(nome='User', email=email, tipo=tipo)
    user.set_senha(password)
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email, senha):
    return client.post('/login', data={'email': email, 'senha': senha})


def test_coupon_creation_and_application(client):
    with client.application.app_context():
        user = create_user()
        produto = Produto(nome='Produto Teste', preco=100)
        db.session.add(produto)
        db.session.commit()
        prod_id = produto.id
    login(client, 'user@example.com', '123')
    data = {'codigo': 'DESC10', 'tipo': 'percentual', 'valor': 10, 'limite': 5}
    resp = client.post('/api/cupom/criar', data=json.dumps(data), content_type='application/json')
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True
    client.get(f'/adicionar_ao_carrinho/{prod_id}')
    resp = client.post('/api/carrinho/aplicar_cupom', data=json.dumps({'codigo': 'DESC10'}), content_type='application/json')
    assert resp.status_code == 200
    resp = client.get('/carrinho')
    html = resp.get_data(as_text=True)
    assert 'Desconto (DESC10)' in html
    assert '96.75' in html
