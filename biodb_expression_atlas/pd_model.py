## Creates PD_atlas database

import pandas as pd
from collections import defaultdict

## SQLALchemy model
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, ForeignKey, Float, create_engine

# expression_atlas
from .startup import datafile_paths

Base = declarative_base()

con_str ='mysql+pymysql://pd_user:pd_password@localhost/pd_atlas'
engine = create_engine(con_str)
session = Session(engine)

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


# create database
class PD_db:
    """ Create and Import data in the database """
    
    def __init__(self, engine, Base):
        self.Base = Base
        self.engine = engine
        self.parkinson_exp = None
        self.exp_tables = None # dict
    
    def create_database(self, data_folder):
        self.Base.metadata.drop_all(self.engine)
        self.Base.metadata.create_all(self.engine)
        self._import_data(data_folder)
    
    def _experiment_groups(self):
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
        self.parkinson_exp = parkinson_exp
    
    def _experiment_tables(self):
        # Create tables for each experiment
        # Each experiment has different groups with pvalue, log2foldchange for same genes
        # hence, create a small tables with gene name, pvalue and log2foldchange for every group in a experiment
        # and these small tables to one big table of single experiment
        # concate tables of different groups with same experiment to one experiment table

        # store tables (to insert in database)
        exp_tables = {}

        for path in datafile_paths:
            # read data files
            data = pd.read_csv(path, sep='\t')
            data.dropna(subset='Gene Name', inplace=True, axis=0)
            exp_name = os.path.basename(path).split('_')[0]
            # find the groups with same the experiment
            groups = self.parkinson_exp[self.parkinson_exp['experiment'] == exp_name]
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
        
        self.exp_tables = exp_tables
        print(self.exp_tables[exp_name])
        print(self.parkinson_exp)
    
    def _import_data(self, data_folder):
        self._experiment_groups()
        self._experiment_tables()
        self.parkinson_exp.to_sql('parkinson_experiment', self.engine, if_exists='append')
        for name, table in self.exp_tables.items():
            table.to_sql(name, self.engine, if_exists='replace')

### wrapper function to create the database
def Create_Database(data_folder):
    obj = PD_db(engine=engine, Base=Base)
    obj.create_database(data_folder)
