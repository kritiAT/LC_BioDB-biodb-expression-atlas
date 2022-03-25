import os
import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine

from .startup import datafile_paths
from .startup import create_new_database

create_new_database()
Base = declarative_base()

con_str ='mysql+pymysql://pd_user:pd_password@localhost/pd_atlas'
engine = create_engine(con_str)
session = Session(engine)


class Experiments(Base):
    """Class definition for parkinson_experiment table."""
    __tablename__ = 'parkinson_experiment'
    exp_id = Column(Integer,primary_key = True)
    experiment_id = Column(String(30),nullable=False)
    group_id = Column(String(30),nullable=False)

class E_MEXP_1416(Base):
    """Class definition for 'E_MEXP_1416' table."""
    __tablename__ = 'E_MEXP_1416'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(30),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.exp_id'), nullable=False)

class E_GEOD_20333(Base):
    """Class definition for 'E_GEOD_20333' table."""
    __tablename__ = 'E_GEOD_20333'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(30),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.exp_id'), nullable=False)

class E_GEOD_7307(Base):
    """Class definition for 'E_GEOD_7307' table."""
    __tablename__ = 'E_GEOD_7307'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(30),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.exp_id'), nullable=False)
    
class E_GEOD_7621(Base):
    """Class definition for 'E_GEOD_7621' table."""
    __tablename__ = 'E_GEOD_7621'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(30),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.exp_id'), nullable=False)
    
class E_GEOD_20168(Base):
    """Class definition for 'E_GEOD_20168' table."""
    __tablename__ = 'E_GEOD_20168'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(30),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('parkinson_experiment.exp_id'), nullable=False)


class PD_db:
    """ Create and Import data in the database """
    def __init__(self, engine, Base):
        self.Base = Base
        self.engine = engine
        self.parkinson_exp = None
        self.exp_tables = None
    

    def create_database(self):
        self.Base.metadata.drop_all(self.engine)
        self.Base.metadata.create_all(self.engine)
        self._import_data()
    
    def _experiment_groups(self):
        exp_group = {'E-MEXP-1416' : ['g2_g1', 'g4_g3'],
                     'E-GEOD-20333' : ['g2_g1'],
                     'E-GEOD-7307' : ['g83_g17','g82_g16', 'g72_g15', 'g63_g14', 'g48_g13'],
                     'E-GEOD-7621' : ['g1_g2'],
                     'E-GEOD-20168' : ['g2_g1']}
                     
        # table with all experiments and groups
        parkinson_exp = pd.DataFrame(exp_group.items(), columns=['experiment_id', 'group_id'])
        parkinson_exp = parkinson_exp.explode('group_id', ignore_index=True)
        parkinson_exp.set_axis([i for i in range(1, len(parkinson_exp) + 1)], axis=0, inplace=True)
        parkinson_exp.rename_axis('exp_id', inplace=True)
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
            groups = self.parkinson_exp[self.parkinson_exp['experiment_id'] == exp_name]
            # concat group tables
            for exp_id, (exp_name, group) in groups.iterrows():
                colnames = {'Gene Name' : 'gene_name', 
                            f'{group}.p-value' : 'p_value',
                            f'{group}.log2foldchange' : 'log2foldchange'}
                df = data[['Gene Name', f'{group}.p-value', f'{group}.log2foldchange']].copy(deep=False)
                df.rename(columns=colnames, inplace=True)
                df['experiment_group'] = [exp_id for i in range(len(df))]
                if exp_name in exp_tables:
                    group_df = exp_tables[exp_name].copy(deep=False)
                    exp_tables[exp_name] = pd.concat([group_df, df])
                else:
                    exp_tables[exp_name] = df
        
        self.exp_tables = exp_tables
    
    def _import_data(self):
        # Imports data from dataframe into database
        self._experiment_groups()
        self._experiment_tables()
        self.parkinson_exp.to_sql('parkinson_experiment', self.engine, if_exists='append', index=True)
        for name, table in self.exp_tables.items():
            table.set_axis([i for i in range(1, len(table) + 1)], axis=0, inplace=True)
            table.rename_axis('id', inplace=True)
            table.to_sql(name.lower().replace('-', '_'), self.engine, if_exists='append', index=True)


### wrapper function to create the database
def database():
    obj = PD_db(engine=engine, Base=Base)
    obj.create_database()