# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bisect
import time, requests, os, xlrd, sys
from datetime import timedelta,date
pd.set_option('precision',3)

hd_date=pd.datetime.today()#历史表的统计结束日期，软件初始默认为当天。pd.datetime.today()'2010-10-4'
#指定日期的指数PE（等权重）

def calc_state(data):#对当前百分位状态的评估
    if data < 10.0:
        return u'极度低估'
    elif 10 <= data  and data < 20:
        return u'低估'
    elif 20 <= data  and data < 40:
        return u'正常偏低'
    elif 40 <= data  and data < 60:
        return u'正常'
    elif 60 <= data  and data < 80:
        return u'正常偏高'
    elif 80 <= data  and data < 90:
        return u'高估'
    elif 90 <= data:
        return u'极度高估'

def get_index_pe_pb_date(code,date):
    '''指定日期的指数PE_PB（等权重）'''
    stocks = get_index_stocks(code, date)#返回指数对应的股票代码
    q = query(valuation).filter(valuation.code.in_(stocks))
    df = get_fundamentals(q, date)#获取指数下对应股票的具体信息列表
    if len(df)>0:
        pe = len(df)/sum([1/p if p>0 else 0 for p in df.pe_ratio])#求等权重pe，len（df）返回股票数
        pb = len(df)/sum([1/p if p>0 else 0 for p in df.pb_ratio])
        return (round(pe,2), round(pb,2))#返回求整数后的pe和pb值
    else:
        return float('NaN')
    
 
#指数历史PEPB
def get_index_pe_pb(code, start_date=None, end_date=None):
    '''指数历史PE_PB'''
    if start_date is None:
        start_date = get_security_info(code).start_date
        if start_date < date(2005,1,1):
            start_date = date(2005,1,1)
    if end_date is None:
        end_date =pd.datetime.today() - timedelta(1)#结束日期为程序运行日期的前一天
    x = get_price(code, start_date=start_date, end_date=end_date, frequency='daily', fields='close')
    date_list = x.index.tolist()
#     print date_list
    pe_list = []
    pb_list = []
    for d in date_list: #交易日
        pe_pb = get_index_pe_pb_date(code,d)
        pe_list.append(pe_pb[0])
        pb_list.append(pe_pb[1])
    df = pd.DataFrame({'PE': pd.Series(pe_list, index=date_list),
                        'PB': pd.Series(pb_list, index=date_list)})
    return df #返回指数“日期，pe，pb”的列表


def get_hs_data(index_choose,data_root='./'):
    '''增量更新沪深指数估值数据'''
    for code in index_choose:
#         print u'正在计算:', code
        data_path = '%s%s_pe_pb.csv'%(data_root,convert_code(code))
        if os.path.exists(data_path):#增量更新
            df_pe_pb = pd.DataFrame.from_csv(data_path)
            start_date = df_pe_pb.iloc[-1].name + timedelta(1)
            df_pe_pb = pd.concat([df_pe_pb, get_index_pe_pb(code, start_date)]) 
        else:#初次计算
            print 'init'
            df_pe_pb = get_index_pe_pb(code)
        df_pe_pb.to_csv(data_path)
        
def convert_code(code):#代码显示模式变更
    if code.endswith('XSHG'):
        return 'sh' + code[0:6]
    elif code.endswith('XSHE'):
        return 'sz' + code[0:6]   
        
        
def get_hs_data(index_list,data_root='./'):
    '''增量更新沪深指数估值数据'''
    for code in index_list:
#         print u'正在计算:', code
        data_path = '%s%s_pe_pb.csv'%(data_root,convert_code(code))
        if os.path.exists(data_path):#增量更新
            df_pe_pb = pd.DataFrame.from_csv(data_path)
            start_date = df_pe_pb.iloc[-1].name + timedelta(1)
            df_pe_pb = pd.concat([df_pe_pb, get_index_pe_pb(code, start_date)]) 
        else:#初次计算
            print 'init'
            df_pe_pb = get_index_pe_pb(code)
        df_pe_pb.to_csv(data_path)
