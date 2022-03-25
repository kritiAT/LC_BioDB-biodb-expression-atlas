import os
import pandas as pd
import pymysql
from getpass import getpass
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine
from .startup import datafile_paths

Base = declarative_base()

con_str ='mysql+pymysql://pd_user:pd_password@localhost/pd_atlas'
engine = create_engine(con_str)
session = Session(engine)


class ComparisonGroup(Base): 
    """Class definition for 'comparison_group' table."""
    __tablename__ = 'comparison_group' 
    id = Column(Integer,primary_key = True)  
    experiment_id = Column(String(30),nullable=False)
    group_id = Column(String(30),nullable=False)

class Expression(Base):
    """Class definition for 'expression' table."""
    __tablename__ = 'expression'
    id = Column(Integer,primary_key = True)
    gene_name = Column(String(30),nullable=False)
    p_value = Column(Float)
    log2foldchange = Column(Float,nullable=False)
    experiment_group = Column(Integer, ForeignKey('comparison_group.id'), nullable=False)
 
class PD_db:
    """ Create and Import data in the database """
    def __init__(self, engine, Base):
        self.Base = Base
        self.engine = engine
        self.parkinson_exp = None
        self.exp_tables = None
    
    def create_database(self):
        self.create_new_db()
        self.Base.metadata.drop_all(self.engine)
        self.Base.metadata.create_all(self.engine)
        self._import_data()

    def create_new_db(self):
        root_password = getpass(prompt='MySQL root password: ')

        conn_root = pymysql.connect(host='localhost',
                                    user='root',
                                    password=root_password,
                                    charset='utf8mb4')
        cursor_root = conn_root.cursor()
    
        cursor_root.execute("DROP DATABASE IF EXISTS pd_atlas")
        cursor_root.execute("CREATE DATABASE IF NOT EXISTS pd_atlas")
        cursor_root.execute("CREATE USER IF NOT EXISTS 'pd_user'@'localhost' IDENTIFIED BY 'pd_password'")
        cursor_root.execute("GRANT ALL ON `pd_atlas`.* TO 'pd_user'@'localhost'")
        cursor_root.execute("FLUSH PRIVILEGES")
        conn_root.close()

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
        parkinson_exp.rename_axis('id', inplace=True)
        self.parkinson_exp = parkinson_exp
    
    def _experiment_tables(self):
        # Create tables for each experiment
        # Each experiment has different groups with pvalue, log2foldchange for same genes
        # hence, create a small tables with gene name, pvalue and log2foldchange for every group in a experiment
        # and these small tables to one big table of single experiment
        # concate tables of different groups with same experiment to one experiment table

        # store tables (to insert in database)
        exp_tables = pd.DataFrame(columns=['gene_name', 'p_value', 'log2foldchange', 'experiment_group'])

        for path in datafile_paths:
            # read data files
            data = pd.read_csv(path, sep='\t')
            data.dropna(subset='Gene Name', inplace=True, axis=0)
            exp_name = os.path.basename(path).split('_')[0]
            # find the groups with same the experiment
            groups = self.parkinson_exp[self.parkinson_exp['experiment_id'] == exp_name]
            # concat group tables
            for index, (exp_id, group) in groups.iterrows():
                colnames = {'Gene Name' : 'gene_name',
                            f'{group}.p-value' : 'p_value',
                            f'{group}.log2foldchange' : 'log2foldchange'}
                df = data[['Gene Name', f'{group}.p-value', f'{group}.log2foldchange']].copy(deep=False)
                df.rename(columns=colnames, inplace=True)
                df['experiment_group'] = [index for i in range(len(df))]
                exp_tables = pd.concat([exp_tables, df], ignore_index=True)

        exp_tables.index += 1
        exp_tables.rename_axis('id', inplace=True)
        
        self.exp_tables = exp_tables
    
    def _import_data(self):
        # Imports data from dataframe into database
        self._experiment_groups()
        self._experiment_tables()
        self.parkinson_exp.to_sql('comparison_group', self.engine, if_exists='append', index=True)
        self.exp_tables.to_sql('expression', self.engine, if_exists='append', index=True)


### wrapper function to create the database
def database():
    obj = PD_db(engine=engine, Base=Base)
    obj.create_database()