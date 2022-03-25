from webbrowser import Grail
from biodb_expression_atlas.web.models import atlas
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from biodb_expression_atlas.web.models.atlas import *
from typing import Dict
class PD_Atlas:
    '''Class for extracting upregulated and downregulated genes from Expression Atlas related to Parkinson Disease.'''
    @staticmethod
    def get_up_and_down_regulated_hgnc_symbols(
                 experiment_id: str,
                 group_id: str,
                 threshold_p_value : float = 0.05,
                 threshold_log2fold_change: float = 1) -> Dict[list, list]:
                 
        '''Queries the database according to the input values
        
        Parameters
        ----------
        experiment_id: str
            Gene experiment id of Expression Atlas 
        group_id: str
            Group id of variables
        threshold_p_value: float
            Threshold of p-value, 0.05 by default
        threshold_log2fold_change: float
            Threshold of log 2 fold change, 1 by default
        
        Returns
        -------
        Dict[list, list]
            a dictionary of two lists(genes_up and genes_down)
        '''

        # check whether experiment id and group id are correct
        experiment_groups = {'E-MEXP-1416' : ['g2_g1', 'g4_g3'],
             'E-GEOD-20333' : ['g2_g1'],
             'E-GEOD-7307' : ['g83_g17','g82_g16', 'g72_g15', 'g63_g14', 'g48_g13'],
             'E-GEOD-7621' : ['g1_g2'],
             'E-GEOD-20168' : ['g2_g1']}
        if experiment_id not in experiment_groups.keys():
            raise ValueError ("Incorrect experiment ID for Parkinson's disease")
        elif group_id not in experiment_groups[experiment_id]:
            raise ValueError (f"Incorrect group ID for experiment {experiment_id}")        

        # map_dict = {'E-MEXP-1416' : E_MEXP_1416,
        #      'E-GEOD-20333' : E_GEOD_20333,
        #      'E-GEOD-7307' : E_GEOD_7307,
        #      'E-GEOD-7621' : E_GEOD_7621,
        #      'E-GEOD-20168' : E_GEOD_20168}
        
        # connect to database
        con_str ='mysql+pymysql://pd_user:pd_password@localhost/pd_atlas'
        engine = create_engine(con_str)
        session = Session(engine)
        
        # SQL Query
        experiment_group_id = session.query(ComparisonGroup).filter(ComparisonGroup.experiment_id==experiment_id, ComparisonGroup.group_id==group_id).one()
        id = experiment_group_id.exp_id
        
        genes_up = session.query(Expression.gene_name).filter(Expression.experiment_group==id, Expression.p_value < threshold_p_value, \
                    Expression.log2foldchange > threshold_log2fold_change).order_by(Expression.log2foldchange).all()
        genes_up = [g[0] for g in genes_up]
        
        genes_down = session.query(Expression.gene_name).filter(Expression.experiment_group==id, Expression.p_value < threshold_p_value, \
                    Expression.log2foldchange < - threshold_log2fold_change).order_by(Expression.log2foldchange).all()
        genes_down = [g[0] for g in genes_down]
        
        return {'up':genes_up,'down':genes_down}
