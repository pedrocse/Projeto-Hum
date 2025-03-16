import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Configurações do banco de dados
engine = create_engine('sqlite:///notas_alunos.db')
Base = declarative_base()


# Definição das tabelas
class Aluno(Base):
    __tablename__ = 'alunos'
    id = Column(Integer, primary_key=True)
    numero = Column(Integer, unique=True)
    ra = Column(String, nullable=True)
    nome = Column(String)
    email = Column(String, nullable=True)
    notas = relationship("Nota", back_populates="aluno")


class Disciplina(Base):
    __tablename__ = 'disciplinas'
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)
    notas = relationship("Nota", back_populates="disciplina")


class Nota(Base):
    __tablename__ = 'notas'
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id'))
    disciplina_id = Column(Integer, ForeignKey('disciplinas.id'))
    valor = Column(Float)

    aluno = relationship("Aluno", back_populates="notas")
    disciplina = relationship("Disciplina", back_populates="notas")


# Criar tabelas no banco
Base.metadata.drop_all(engine)  # Limpar o banco antes de criar
Base.metadata.create_all(engine)

# Carregar dados do Excel
df = pd.read_excel('NotasT3BD.xlsx')

# Iniciar sessão
Session = sessionmaker(bind=engine)
session = Session()

# Inserir alunos (verificando duplicatas)
for _, row in df.iterrows():
    aluno_existente = session.query(Aluno).filter_by(numero=row['Numero']).first()
    if not aluno_existente:
        aluno = Aluno(
            numero=row['Numero'],
            ra=row['RA'] if pd.notna(row['RA']) else None,
            nome=row['Nome'],
            email=row['email'] if pd.notna(row['email']) else None
        )
        session.add(aluno)
session.commit()

# Inserir disciplinas
disciplinas = []
for col in df.columns[4:]:
    disciplina = Disciplina(nome=col)
    disciplinas.append(disciplina)
session.add_all(disciplinas)
session.commit()

# Mapear IDs de alunos e disciplinas
aluno_dict = {a.numero: a.id for a in session.query(Aluno).all()}
disciplina_dict = {d.nome: d.id for d in session.query(Disciplina).all()}

# Inserir notas
notas = []
for _, row in df.iterrows():
    for disciplina in df.columns[4:]:
        nota = Nota(
            aluno_id=aluno_dict[row['Numero']],
            disciplina_id=disciplina_dict[disciplina],
            valor=row[disciplina] if pd.notna(row[disciplina]) else None
        )
        notas.append(nota)
session.add_all(notas)
session.commit()