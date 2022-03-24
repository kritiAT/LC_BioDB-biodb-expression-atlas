from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine
import pandas as pd
import pymysql
from .startup import datafile_paths

con_str ='mysql+pymysql://pd_user:pd_password@localhost/pd_atlas'
engine = create_engine(con_str)

Base = declarative_base()

class Experiments(Base):
    __tablename__ = 'parkinson_experiment'
    id = Column(Integer,primary_key = True)
    experiment_id = Column(String(50),nullable=False)
    group_id = Column(String(50),nullable=False)

class Experiment_1(Base):
    __tablename__ = 'E-MEXP-1416'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(50),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.id'), nullable=False)

class Experiment_2(Base):
    __tablename__ = 'E-GEOD-20333'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(50),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.id'), nullable=False)

class Experiment_3(Base):
    __tablename__ = 'E-GEOD-7307'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(50),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.id'), nullable=False)
    
class Experiment_4(Base):
    __tablename__ = 'E-GEOD-7621'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(50),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.id'), nullable=False)
    
class Experiment_5(Base):
    __tablename__ = 'E-GEOD-20168'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(50),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.id'), nullable=False)


def create_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    _import_data()

def _experiment_groups():
    exp_group = {'E-MEXP-1416' : ['g2_g1', 'g4_g3'],
                    'E-GEOD-20333' : ['g2_g1'],
                    'E-GEOD-7307' : ['g83_g17','g82_g16', 'g72_g15', 'g63_g14', 'g48_g13'],
                    'E-GEOD-7621' : ['g1_g2'],
                    'E-GEOD-20168' : ['g2_g1']}
    # table with all experiments and groups
    parkinson_exp = pd.DataFrame(exp_group.items(), columns=['experiment', 'group_id'])
    parkinson_exp = parkinson_exp.explode('group_id')
    parkinson_exp.reset_index(inplace=True, drop=True)
    parkinson_exp.set_axis([i for i in range(1, len(parkinson_exp) + 1)], axis=0, inplace=True)
    parkinson_exp.index.name ='id'
    return parkinson_exp

def _experiment_tables(self):
    # Create tables for each experiment
    # Each experiment has different groups with pvalue, log2foldchange for same genes
    # hence, create a small tables with gene name, pvalue and log2foldchange for every group in a experiment
    # and these small tables to one big table of single experiment
    # concate tables of different groups with same experiment to one experiment table

    # store tables (to insert in database)
    exp_tables = {}
    parkinson_exp = _experiment_groups()

    for path in datafile_paths:
        # read data files
        data = pd.read_csv(path, sep='\t')
        data.dropna(subset='Gene Name', inplace=True, axis=0)
        exp_name = os.path.basename(path).split('_')[0]
        # find the groups with same the experiment
        groups = parkinson_exp[parkinson_exp['experiment'] == exp_name]
        # concat group tables
        for index, (exp_name, group) in groups.iterrows():
            colnames = {f'{group}.p-value' : 'p-value',
                        f'{group}.log2foldchange' : 'log2foldchange'}
            df = data[['Gene Name', f'{group}.p-value', f'{group}.log2foldchange']].copy(deep=False)
            df.rename(columns=colnames, inplace=True)
            df['exp_id'] = [index for i in range(len(df))]          # change column name
            if exp_name in exp_tables:
                group_df = exp_tables[exp_name].copy(deep=False)
                exp_tables[exp_name] = pd.concat([group_df, df])
                exp_tables[exp_name].set_axis([i for i in range(1, len(exp_tables[exp_name]) + 1)], axis=0, inplace=True)
                exp_tables[exp_name].index.name ='id'
            else:
                exp_tables[exp_name] = df
                exp_tables[exp_name].set_axis([i for i in range(1, len(exp_tables[exp_name]) + 1)], axis=0, inplace=True)
                exp_tables[exp_name].index.name ='id'
    
    return exp_tables
    
def _import_data():
    parkinson_exp = _experiment_groups()
    exp_tables = _experiment_tables()

    parkinson_exp.to_sql('parkinson_experiment', engine, if_exists='append')
    for name, table in exp_tables.items():
        table.to_sql(name, engine, if_exists='append')
