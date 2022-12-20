from ift6758.data.Feature_Engineering2 import tidyData, getPreviousEvent
from ift6758.data.Feature_Engineering1 import combineAllFeatures
from sklearn import preprocessing
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd


def test_data_loader() :
    testset = pd.read_csv('../notebooks/test_set.csv')
    test_featureeng1= combineAllFeatures(testset)
    test_set_featureeng2= getPreviousEvent(test_featureeng1)
    test_set_featureeng2["rebound"].fillna(value=0)
    test_set_featureeng2['rebound'].astype(int)
    FinalDf = test_set_featureeng2[['Is_goal','period','periodSeconds',
              'last_EventType',
              'last_period',
             # 'last_periodTime',(not needed dince we have lastperiodseconds)
              'last_eventxCoord','last_eventyCoord',
             'last_shotType',
              'last_periodSeconds','last_Distance_from_net',
              'last_Angle_from_net',
              'time_from_last_event',
              'distance_from_last_event','rebound','change_in_angle','speed']]
    obj_df=FinalDf.select_dtypes(include=['object']).copy()
    FinalDf=FinalDf.drop(obj_df.columns, axis=1)
    obj_df=obj_df.apply(preprocessing.LabelEncoder().fit_transform)
    Frame=pd.concat([FinalDf,obj_df],axis=1)
    imp_mean = SimpleImputer(missing_values=np.nan, strategy='median')
    imp_mean.fit(FinalDf)
    Transformed_Values=imp_mean.transform(FinalDf)
    TransformedDf = pd.DataFrame(Transformed_Values, index=FinalDf.index, columns=FinalDf.columns)
    TransformedDf_=TransformedDf.drop("period",axis=1)
    test_X = TransformedDf_.drop('Is_goal',axis=1)
    return test_X