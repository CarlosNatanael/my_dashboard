from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    console = db.Column(db.String(50), nullable=False)
    console_icon = db.Column(db.String(200), nullable=True) 
    ra_id = db.Column(db.Integer, nullable=True)
    image_icon = db.Column(db.String(100), nullable=True)

    status = db.Column(db.String(50), default='claim')
    progress = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUS_MAP = {
        # Fase 0: Planejamento Futuro
        'wishlist': ('Lista de Desejos (Futuro)', 'dark'),

        # Fase 1: Início
        'claim': ('Claim Ativa', 'secondary'),
        'ram': ('Cavando/Inspecionando RAM', 'info'),
        
        # Fase 2: Desenvolvimento
        'logic': ('Desenvolvendo Achievements', 'primary'),
        'badge': ('Desenvolvendo Badges/Ícones', 'primary'),
        
        # Fase 3: Revisão e Apoio Externo
        'writing': ('Aguardando Revisão de Escrita', 'warning'),
        'art_team': ('Aguardando Equipe de Arte', 'warning'),
        'playtest': ('Enviado p/ Player-Tester', 'warning'),
        
        # Fase 4: Testes Finais
        'testing': ('Testando Achievements', 'light text-dark'),
        'pre_release': ('Últimos Testes (Pré-Lançamento)', 'success'),
        
        # Fase 5: Produção
        'published': ('Publicado / Ativo', 'success'),
        'tickets': ('Atendendo Tickets', 'danger'),
        'revision': ('Revisão de Conjunto', 'danger')
    }

    @property
    def status_label(self):
        return self.STATUS_MAP.get(self.status, (self.status, 'secondary'))[0]

    @property
    def status_color(self):
        return self.STATUS_MAP.get(self.status, ('secondary', 'secondary'))[1]

    def __repr__(self):
        return f'<Claim {self.title} - {self.status}>'