"""Main module."""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .pd_model import Experiments

class Group1:
    '''Class for extracting upregulated and downregulated genes from Expression Atlas.'''

    @staticmethod
    def get_up_and_down_regulated_hgnc_symbols(
                 experiment_id: str,
                 group_id: str,
                 threshold_p_value : float = 0.05,
                 threshold_log2fold_change: float=1) -> Dict[list, list]:
        '''Queries the database according to the input values
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

            
        con_str ='mysql+pymysql://pd_user:pd_password@localhost/pd_atlas'
        engine = create_engine(con_str)
        session = Session(engine)
        
        # SQL query   
        experiment_group_id = session.query(Experiments).filter(Experiments.experiment_id==experiment_id, Experiments.group_id==group_id).one()
        
        genes_up = session.query(Experiments).join(experiment_id).filter(experiment_id.p_value < threshold_p_value, experiment_id.log2foldchange > threshold_log2fold_change).all()
        genes_down = session.query(Experiments).join(experiment_id).filter(experiment_id.p_value < threshold_p_value, experiment_id.log2foldchange < - threshold_log2fold_change).all()
        
        return {'up':genes_up,'down':genes_down}
