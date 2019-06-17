# coding=utf-8
"""
@version:   $ID$
@author:    hanxu (Sy1507522)
            liujiawei (Sy1507518)
@license:
@contact:   hanxubuaa11107@gmail.com,liujiawei0524@buaa.edu.com
"""

import sqlite3, random, threading, time, _thread
from tkinter import *
##import Tkinter as tk
from tkinter import messagebox
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class User:
    """
    @Class describe��  �û��ࡢ�����������㡣�������е�ǰ�û�����,ֱ������ֲ�����
    @private param:     __username      �û���
                        __balance       ��Ĭ��ֵΪ10000
                        __totalProperty ���ʲ���Ĭ��ֵΪ10000
                        __profit        ӯ����Ĭ��ֵΪ0
                        __stockProperty ��ǰ�û���Ʊ�ʲ���Ĭ��ֵΪ0
                        __oriPro        �û���ʼ�Ʋ�,Ĭ��ֵΪ10000
    """
    __username = ''
    __balance = 10000  # ���
    __totalProperty = 10000  # ���ʲ�
    __profit = 0  # ӯ��
    __stockProperty = 0  # ��ǰ�û���Ʊ�ʲ�
    __oriPro = 10000  # �û���ʼ�Ʋ�

    def __init__(self, name):
        self.__username = name

    def calBalance(self):
        """��ѯ�����û����"""
        db = Database('testDB.db', self.__username)
        db.getLinkedUser(self.__username)
        temp = db.getUserCurrentmoney()
        return temp

    def calToatalProperty(self):
        """��ѯ�����û����ʲ�"""
        db = Database('testDB.db', self.__username)
        db.getLinkedUser(self.__username)
        temp = db.getUserCurrentprop()
        return temp

    def calPrfLoss(self):
        """��ѯ���ص�ǰ����"""
        return self.calToatalProperty() - self.__oriPro

    def calStockProp(self):
        """��ѯ�����û���Ʊ�ʲ�"""
        db = Database('testDB.db', self.__username)
        db.getLinkedUser(self.__username)
        temp = db.getUserStockprop()
        return temp

    def update(self):
        self.__balance = self.calBalance()
        self.__totalProperty = self.calToatalProperty()
        self.__profit = self.calPrfLoss()
        self.__stockProperty = self.calStockProp()
        return True

    def buyOneStock(self, stockname, stocknum):
        """����һ֧��Ʊ
            :param stockname:   �����Ʊ����
            :param stocknum:    ��������
            :return:            BOOL
            """
        db = Database('testDB.db', self.__username)
        # �ж��Ƿ������㹻\�û���Ǯ��
        money = stocknum * db.getStockPrice(stockname)
        flag1 = (bool)(db.getUserCurrentmoney() > money)
        flag2 = (bool)(db.getStockBalance(stockname) > stocknum)

        if flag1 and flag2:
            db.changeUserStocknum(self.__username, stockname, stocknum)
            db.changeStockBalance(stockname, -stocknum)
            db.changeUserCurrentmoney(-money)
            return True
        else:
            askokcancel('������Ч', '��Ʊ����������̫���ˣ������¹���')
            return False

    def sellOneStock(self, stockname, stocknum):
        """���һ֧��Ʊ
                :param stockname:   �����Ʊ����
                :param stocknum:    ��������
                :return:            BOOL
                """
        db = Database('testDB.db', self.__username)
        money = stocknum * db.getStockPrice(stockname)
        flag1 = (bool)(db.getUserStocknum(self.__username, stockname) > stocknum)
        if flag1:
            db.changeUserStocknum(self.__username, stockname, stocknum)
            db.changeStockBalance(stockname, -stocknum)
            db.changeUserCurrentmoney(-money)
            return True
        else:
            askokcancel('������Ч', '��û����ô���Ʊ�������¹���')
            return False
        return True

    def getUsername(self):
        """
        :return:    string�û���
        """
        self.update()
        return self.__username

    def getBalance(self):
        """
        :return:    float�û��ֽ����
        """
        self.update()
        db = Database('testDB.db', self.__username)
        self.__balance = db.getUserCurrentmoney()
        return self.__balance

    def getTotalProperty(self):
        """
        :return:    float�û��������ʲ�
        """
        self.update()
        return self.__totalProperty

    def getProfitOrLoss(self):
        """
        :return:    float�û����ʲ�ӯ��
        """
        self.update()
        return round(self.__profit, 2)

    def getStockProp(self):
        """
        :return:    float�û���Ʊ�ܶ�
        """
        self.update()
        return self.__stockProperty

    def drawUserExchange(self, figure):
        """
        �����ڻ�������ʾ�û����еĹ�Ʊ��������ʾ��ʽΪ��״ͼ
        :param figure:  Figure
        :return:
        """
        db = Database('testDB.db', self.__username)
        stocknamelist = db.getStocknameList()
        userstocknumlist = db.getUserStocknnumlist(self.__username)
        width = 0.5
        a = figure.add_subplot(111)
        ind = np.arange(1, len(stocknamelist) + 1, 1)
        a.cla()
        a.bar(ind - width / 2, userstocknumlist, width, color='green')
        a.set_xticks(ind)
        a.set_xticklabels(stocknamelist)
        a.set_xlabel(u'Stock ID')
        a.set_ylabel(u'Stock num')

    def getStockholdingMsg(self):
        """
        :return:    string �û����й�Ʊ������Ϣ
        """
        db = Database('testDB.db', self.__username)
        return db.getUserStockholdingStr(self.__username)


class Stock:
    """
    @Class describe��  ��Ʊ�ࡢ�����������㡣�������й�Ʊ�г��Ĳ���,ֱ������ֲ�����
    """

    def __init__(self):
        return

    def showStockprice(self, f):
        """
        �ڻ���������״ͼ����ʽ��ʾ���й�Ʊ��Ϣ�۸񣬰����˹�Ʊ�۸񸡶�����
        :param f:   Figure
        :return:
        """
        db = Database('testDB.db', '')
        stocknamelist = db.getStocknameList()
        # ��Ʊ�۸񸡶�
        self.floatStock()
        stockpricelist = db.getStockpriceList()
        a = f.add_subplot(111)
        ind = np.arange(1, len(stocknamelist) + 1, 1)
        width = 0.5
        a.cla()
        a.bar(ind - width / 2, stockpricelist, width, color='coral')
        a.set_xticks(ind)
        a.set_xticklabels(stocknamelist)
        a.set_xlabel(u'Stock name')
        a.set_ylabel(u'Stock Price')

        # ����ר��
        # userStocknamelist = db.getUserStocknnumlist()

        # ����ר��
        return True

    def floatStock(self):
        """
        �Թ�Ʊ�г����м۸񸡶�������5%�������
        :return:    Bool
        """
        db = Database('testDB.db', '')
        stocknamelist = db.getStocknameList()
        for n in stocknamelist:
            temp = random.uniform(90, 110) / 100
            price1 = ((float)(db.getStockPrice(n)))
            price = round(price1 * temp, 2)
            a = db.changeStockPrice(n, price)
            # if a:
            #     print 'change stockname:'+ n#+'from' +price1+ 'to'  + price
        return True

    def addNewstock(self, stockname, stockprice, stocknum):
        """
        �ڹ�Ʊ�г�����һ֧��Ʊ
        :param stockname:   ��Ʊ����
        :param stockprice:  ��Ʊ�۸�
        :param stocknum:    ��Ʊ������
        :return:            Bool
        """

        db = Database('testDB.db', '')
        stocknamelist = db.getStocknameList()  # ��ȡ���й�Ʊ���Ƶ�list
        if stockname in stocknamelist:
            return False
        else:
            stocknamelist.append(stockname)
        db.addnewstock(stockname, stockprice, stocknum)
        return True

    def initStock(self):
        """
        �û���Ʊ������
        """
        db = Database('testDB.db', '')
        db.initStock()

    def deleteStock(self, stockName):
        """
        �ڹ�Ʊ�г�����һ֧��Ʊ
        :param stockname:   ��Ʊ����
        :return:            Bool
        """

        db = Database('testDB.db', '')
        stocknamelist = db.getStocknameList()
        if stockName not in stocknamelist:
            return False
        else:
            db.deleteStock(stockName)
        return True





class Database:
    """
    @Class describe��    ���ݿ�����ࡢ�������ݹ���㡣�����������ݿ���ز���,�����������������
    @private param:     __DBname        ���ݿ����ƣ�ͳһΪtestDB.db
                        __username      �û���
                        conn = sqlite3.connect('')  ���ݿ����Ӳ���
                        curs = conn.cursor()        ���ݿ����Ӳ���
                        sql = ''                    ���ݿ⽻��sql���
    """
    DBname = ''
    # __username = 'jiawei'  # ����ר��
    __username = ''
    conn = sqlite3.connect('')
    curs = conn.cursor()
    sql = ''

    def __init__(self, DBname, user):
        """
        ����DataBase
        """
        self.DBname = DBname
        self.__username = user
        self.conn = sqlite3.connect(self.DBname)
        self.curs = self.conn.cursor()
        return

    def getTable(self, tablename):
        """
        ����stockprice����غ���

        """
        return

    def getLinkedStockprice(self):
        """
        ���ӵ�stockprice
        :return:
        """
        self.getTable("stockprice")
        self.conn = sqlite3.connect('testDB.db')
        self.curs = self.conn.cursor()

    def getStockPrice(self, stockname):
        """
        ����stockprice������ȡĳ֧��Ʊ�۸�
        :param stockname:   ��Ʊ����
        :return:            float��Ʊ�۸�
        """
        self.getLinkedStockprice()
        stockprice = 0.0
        sql = 'SELECT * FROM stockPri WHERE stock=? '
        self.curs.execute(sql, (stockname,))
        self.conn.commit()
        value = self.curs.fetchall()
        # ��stockIndex��stockprice.table�з��ص�֧��Ʊ�۸�
        stockprice += value[0][1]
        self.closeDatabase()
        return round(stockprice, 2)

    def getStockTotalnum(self, stockname):
        """
        ����stockprice������ȡĳ֧��Ʊ��������
        :param stockname:   ��Ʊ����
        :return:            int��Ʊ����
        """
        self.getLinkedStockprice()
        sql = 'SELECT * FROM stockPri WHERE stock=? '
        self.curs.execute(sql, (stockname,))
        self.conn.commit()
        value = self.curs.fetchall()
        # ��stockIndex��stockprice.table�з��ص�֧��Ʊ���ܷ�����
        stockTotalnum = value[0][3]
        self.closeDatabase()
        return stockTotalnum

    def getStockBalance(self, stockname):
        """
        ����stockprice������ȡĳ֧��Ʊ�г�����
        :param stockname:   ��Ʊ����
        :return:            int��Ʊʣ������
        """
        self.getLinkedStockprice()
        sql = 'SELECT * FROM stockPri WHERE stock=? '
        self.curs.execute(sql, (stockname,))
        self.conn.commit()
        value = self.curs.fetchall()
        # ��stockIndex��stockprice.table�з��ص�֧��Ʊ��δ��������
        stockbalance = value[0][2]
        self.closeDatabase()
        return round((float)(stockbalance), 2)

    def changeStockBalance(self, stockname, num):
        """
        ����stockprice��������ĳ֧��Ʊ�������
        :param stockname:   ��Ʊ����
        :param num:         ��Ʊ����
        :return:            Bool
        """
        temp = int(self.getStockBalance(stockname))
        temp += num
        # ��stockIndex��stockprice.table��д��Ϊ��������temp
        if 0 < temp < self.getStockTotalnum(stockname):
            self.getLinkedStockprice()
            sql = 'update stockPri set num=? where stock=?'
            self.curs.execute(sql, (temp, stockname))
            self.conn.commit()
            self.closeDatabase()
            return True
        else:
            self.closeDatabase()
            return False

    def changeStockPrice(self, stockname, price):
        """
        ����stockprice��������ĳ֧��Ʊ�۸�
        :param stockname:   ��Ʊ����
        :param price:       ��Ʊ�۸�
        :return:            Bool
        """
        self.getLinkedStockprice()
        # ��stockIndex��stockprice.table��д��Ϊ��������temp
        if 0 < price:
            sql = 'UPDATE stockPri SET price=? WHERE stock=?'
            self.curs.execute(sql, (price, stockname,))
            self.conn.commit()
            self.closeDatabase()
            return True
        else:
            self.closeDatabase()
            return False

    def addnewstock(self, stockname, stockprice, stocknum):
        """
        ����stockprice��������������һ֧��Ʊ
        :param stockname:   ��Ʊ����
        :param stockprice:  ��Ʊ�۸�
        :param stocknum:    ��Ʊ����
        :return:            Bool
        """
        self.getLinkedStockprice()
        sql = 'insert into stockPri (stock,price,num,totalnum) values(?,?,?,?)'
        self.curs.execute(sql, (stockname, stockprice, stocknum, stocknum))
        sql1 = 'insert into ' + self.__username + '(stock,num) values(?,?)'
        self.curs.execute(sql1, (stockname, 0))
        self.conn.commit()
        self.closeDatabase()
        return True

    def initStock(self):
        """
        ����userProp������λ
        """
        stocknameList = self.getStocknameList()
        self.getLinkedStockprice()
        sql0 = 'update userProp set currentProp=? where username=?'
        self.curs.execute(sql0, (10000, self.__username))
        sql1 = 'update ' + self.__username + ' set num=0 where stock=?'
        sql2 = 'update userProp set currentMoney=10000 where username=?'
        self.curs.execute(sql2, (self.__username,))
        for n in stocknameList:
            try:
                self.curs.execute(sql1, (n,))
                self.conn.commit()
            except:
                # print('update fail')
                pass
        for n in stocknameList:
            try:
                sql3='select *from stockPri where stock=?'
                self.curs.execute(sql3,(n,))
                value=self.curs.fetchall()
                sql4='update stockPri set num=?'
                self.curs.execute(sql4,(value[0][3]))
                self.conn.commit()
            except:
                print('update fail')
        self.closeDatabase()
                
                
        
        
        
        pass

    def deleteStock(self, stockName):
        """
        ����stockprice,user���������м���һ֧��Ʊ
        :param stockName:   ��Ʊ����
        :return:            Bool
        """
        try:
            self.getLinkedStockprice()

            sql = 'delete from stockPri where stock=?'
            self.curs.execute(sql, (stockName,))
            sql1 = 'delete from ' + self.__username + ' where stock=?'
            self.curs.execute(sql1, (stockName,))

            self.conn.commit()
            self.closeDatabase()
        except:
            return False

    def getStocknameList(self):
        """
        ����stockprice������ȡ��������
        :return:    list����
        """
        self.getLinkedStockprice()
        sql = 'select stock from stockPri'
        self.curs.execute(sql)
        self.conn.commit()
        value = self.curs.fetchall()
        stocknameList = []
        for n in value:
            stocknameList.append(n[0])
        self.closeDatabase()
        return stocknameList

    def getStockpriceList(self):
        """
        ����stockprice������ȡ�۸�����
        :return:    list����
        """
        self.getLinkedStockprice()
        sql = 'select price from stockPri'
        self.curs.execute(sql)
        self.conn.commit()
        value = self.curs.fetchall()
        stockpricelist = []
        for n in value:
            stockpricelist.append(n[0])
        self.closeDatabase()
        return stockpricelist

    """
    ����userx����غ���
    """

    def getLinkedUser(self, username):
        """
        ����user��
        :param username:    �û���
        :return:
        """
        self.getTable(username)
        self.__username = username
        # ��userx������user.table
        self.conn = sqlite3.connect('testDB.db')
        self.curs = self.conn.cursor()

    def getUserStocknum(self, username, stockname):
        """
        ����user������ȡ�û�ĳ֧��Ʊ������
        :param username:    �û�����
        :param stockname:   ��Ʊ����
        :return:            int��Ʊ����
        """
        self.getLinkedUser(username)
        sql = 'select * from ' + self.__username + ' where stock=?'
        self.curs.execute(sql, (stockname,))
        value = self.curs.fetchall()
        userstocknum = value[0][1]
        # ��stockIndex��user.table�з��ص�֧��Ʊ���û�������
        self.closeDatabase()
        return userstocknum

    def getUserStocknnumlist(self, username):
        """
        ����user������ȡ�û���Ʊ����������
        :param username:    ��Ʊ����
        :return:            list����
        """
        self.getLinkedUser(username)
        sql = 'select num from ' + self.__username
        self.curs.execute(sql)
        self.conn.commit()
        value = self.curs.fetchall()
        userStocknumlist = []
        for n in value:
            userStocknumlist.append(n[0])
        self.closeDatabase()
        return userStocknumlist

    def getUserStockpricelist(self):
        """
        ����user������ȡ�û���Ʊ�۸������
        :param username:    ��Ʊ����
        :return:            list����
        """
        self.getLinkedStockprice()
        sql = 'select price from stockPri'
        self.curs.execute(sql)
        self.conn.commit()
        value = self.curs.fetchall()
        userstockpricelist = []
        for n in value:
            userstockpricelist.append(n[0])
        self.closeDatabase()
        return userstockpricelist

    def getUserStockprop(self):
        """
        ����user������ȡ�û���Ʊ���ʲ�
        :param username:    ��Ʊ����
        :return:            float��Ʊ�ʲ�
        """
        userStockpricelist = self.getUserStockpricelist()
        userStocknumlist = self.getUserStocknnumlist(self.__username)
        # i = 0
        # money = 0.0
        # for n in userStocknumlist:
        # money = money + userStockpricelist[i] * userStocknumlist[i]
        # i += 1
        money = sum(map(lambda a: a[0] * a[-1], zip(userStockpricelist, userStocknumlist)))
        return round(money, 2)

    def changeUserStocknum(self, username, stockname, num):
        """
        ����user���������û���Ʊ����
        :param username:    �û���
        :param stockname:   ��Ʊ����
        :param num:         ��Ʊ����
        :return:            list����
        """
        self.getLinkedUser(username)
        temp = int(num)
        temp += self.getUserStocknum(username, stockname)
        # ��stockIndex��stockprice.table��д��Ϊ��������temp
        if -1 < temp < self.getStockTotalnum(stockname):
            self.getLinkedUser(username)
            sql = 'update ' + self.__username + ' set num=? where stock=?'
            self.curs.execute(sql, (temp, stockname))
            self.conn.commit()
            self.closeDatabase()
            return True
        else:
            askokcancel('����ʧ��', '���Ʊ������ʩ������ͷ������')
            self.closeDatabase()
            return False

    def getUserStockholdingStr(self, username):
        """
        ����user������ȡ�û����й�Ʊ����Ϣ
        :param username:    �û���
        :return:            string�ֹ���Ϣ
        """
        userstocknumlist = self.getUserStocknnumlist(username)
        userstocknamelist = self.getStocknameList()
        i = 0
        str1 = ''
        try:
            for n in userstocknamelist:
                str1 = str1 + 'Stock ' + n + ' Num : ' + str(userstocknumlist[i]) + '\n'
                i += 1
            return str1
        except:
            str1 = '�޳��й�Ʊ'
            return str1

    # ����userProp��
    def getLinkedUserprop(self):
        """
        ����userPro�����û��ʲ���
        :return:
        """
        self.getTable('userProp')
        # ������userProp.table
        self.conn = sqlite3.connect('testDB.db')
        self.curs = self.conn.cursor()

    def updateUserCurrentprop(self):
        """
        ����userPro�����������ݿ����û��������ʲ�
        :return:
        """
        temp = self.getUserCurrentmoney() + self.getUserStockprop()
        self.getLinkedUserprop()
        sql = 'update userProp set currentProp=? where username=?'
        self.curs.execute(sql, (temp, self.__username))
        self.conn.commit()
        self.closeDatabase()

    def getUserOriginalprop(self):
        """
        ����userPro������ȡ�û�ԭʼ�ʲ�
        :return:    float�û�ԭʼ�ʲ�
        """
        self.getLinkedUserprop()
        sql = 'SELECT * FROM userProp WHERE username=? '
        self.curs.execute(sql, (self.__username,))
        self.conn.commit()
        value = self.curs.fetchall()
        originalprop = value[0][1]
        self.closeDatabase()
        return round(originalprop, 2)

    def getUserCurrentprop(self):
        """
        ����userPro������ȡ�û���ǰ�ʲ�
        :return:    float�û���ǰ�ʲ�
        """
        self.updateUserCurrentprop()
        self.getLinkedUserprop()
        sql = 'SELECT * FROM userProp WHERE username=? '
        self.curs.execute(sql, (self.__username,))
        self.conn.commit()
        value = self.curs.fetchall()
        currentprop = value[0][2]
        self.closeDatabase()
        return round(currentprop, 2)

    def getUserCurrentmoney(self):
        """
        ����userPro������ȡ�û���ǰ�ʽ�
        :return:    float�û���ǰ�ʽ�
        """
        self.getLinkedUserprop()
        sql = 'SELECT * FROM userProp WHERE username=? '
        self.curs.execute(sql, (self.__username,))
        self.conn.commit()
        value = self.curs.fetchall()
        originalmoney = value[0][3]
        self.closeDatabase()
        return round(float(originalmoney), 2)

    def changeUserCurrentmoney(self, money):
        """
        ����userPro�����ı��û���ǰ�ʽ�
        :param money:   float�ı�Ľ�Ǯ����Ϊ���ӡ���Ϊ���٣�
        :return:        Bool
        """
        self.getLinkedUserprop()
        temp = money + self.getUserCurrentmoney()
        # ��stockIndex��stockprice.table��д��Ϊ��������temp
        if 0 < temp:
            self.getLinkedUserprop()
            sql = 'update userProp set currentMoney=? where username=?'
            self.curs.execute(sql, (temp, self.__username))
            self.conn.commit()
            self.closeDatabase()
            return True
        else:
            self.closeDatabase()
            return False

    def getUseprofit(self):
        """
        ����userPro������ȡ�û�ӯ��
        :return:    float�û�ӯ��
        """
        return self.getUserCurrentprop() - self.getUserOriginalprop()

    """"
    ����namepassword����غ���
    """

    def getLinkedNamepassword(self, name, password):
        """
        ����namepassword������֤name��password�Ƿ�ƥ��
        :param name:        �û���
        :param password:    ����
        :return:            Bool
        """
        self.getTable("namepassword")
        self.conn = sqlite3.connect('testDB.db')
        self.curs = self.conn.cursor()
        sql = 'SELECT * FROM namePassword where name=? '
        try:
            self.curs.execute(sql, (name,))
            value = self.curs.fetchall()
            a = value[0][1]
            if a == password:
                self.__username = name
                self.closeDatabase()
                return True
            else:
                self.closeDatabase()
                return False
        except:
            self.closeDatabase()
            return -1

    def closeDatabase(self):
        self.curs.close()
        self.conn.commit()
        self.conn.close()
        # print 'dtabase closed!'


class ViewFrame():
    """
    @Class describe��    ��ʾ�ࡢ���ڱ��ֲ㡣�������н�����ʾ��ز���,�������������
    @private param:     __flagthread    ��Ʊ�Զ������̱߳�־λ��Ĭ��False
                        __username      �û���
                        __flagexchange = False  ������Ʊ�־λ
                        __flagshowstock = False ������Ʊ�־λ
                        __flagadmin = False     ����Ա��־λ��hanxu�û��ǹ���Ա��������ɾ��Ʊ
    """
    __flagthread = False  # ��Ʊ�Զ������̱߳�־λ
    __flagexchange = False
    __flagshowstock = False
    __flagadmin = False
    __username = ''

    def loginSys(self):
        """
        ��¼����
        :return:
        """
        root = Tk()
        root.title("Wellcome to the StockloginSystem")
        root.geometry('500x200')

        def quit():
            """
            ���ٵ�¼���棬�����Ʊ��ʾҳ��
            :return:
            """
            if self.__flagadmin:
                askokcancel('Welcome��', '����Ա���ˣ���ã����˧��')
            else:
                askokcancel('Welcome��',self.__username + '��ã�')
            root.quit()
            root.destroy()
            if not self.__flagshowstock:
                self.__flagshowstock = True
                self.showStock()

        def enter():
            """
            login��ť��Ӧ��������½�ɹ�������Ʊ��ʾ����
            :return:
            """
            myName = personName.get()
            myPassword = password.get()
            db = Database('testDB.db', self.__username)
            temp = db.getLinkedNamepassword(myName, myPassword)
            if 1 == temp:
                if myName == 'hanxu':
                    self.__flagadmin = True
                self.__username = myName
                self.__flagthread = True
                quit()
            elif 0 == temp:
                contents.delete(1.0, END)
                contents.insert(END, 'wrong password')
            elif -1 == temp:
                contents.delete(1.0, END)
                contents.insert(END, 'this person does not exist')

        """
        ��¼�������
        """
        L1 = Label(root, text="UserID", font=("Arial", 12), width=7, height=2)
        L1.grid(row=0, column=0, sticky=E)
        personName = Entry(root)
        personName.grid(row=0, column=1, sticky=E)

        L2 = Label(root, text="Password", font=("Arial", 12), width=7, height=2)
        L2.grid(row=1, column=0, sticky=E)

        password = Entry(root)
        password.grid(row=1, column=1, sticky=E)
        root.bind('<Return>', enter)
        ButtonEnter = Button(root, text="Login", command=enter, bg="grey", font=("Arial", 12), width=7, height=2)
        ButtonEnter.grid(row=0, column=2, columnspan=2, rowspan=2, sticky=W, padx=30, pady=30)

        contents = Text(root)
        contents.grid(row=2, column=0, columnspan=4, rowspan=1)
        contents.delete(1.0, END)
        contents.insert(END, 'Hello,guys! \nPlease keyboard in your name and passsword to login in')
        # # ����ר��
        # self.__flagthread = True
        # self.__flagshowstock = True
        # self.__username = 'jiawei'
        # self.showStock()
        # #
        mainloop()

    def showStock(self):
        """
        �ɼ���ʾ����
        :return:
        """
        root = Tk()
        root.wm_title('StockMarket     current user : ' + self.__username)
        root.geometry('800x600')
        f = Figure(figsize=(5, 5), dpi=100)

        def quit():
            """
            ���ٵ�ǰ����
            :return:
            """
            root.quit()
            root.destroy()
            self.__flagshowstock = False

        def draw_picture():
            """
            ���ƹ�Ʊ��ʾͼ��
            :return:
            """
            stk = Stock()
            stk.showStockprice(f)
            canvas.draw()

        # ���߳��Զ�ˢ�£���ʱ������
        def autodraw_picture(threadName, delay):
            count = 0
            while 1:
                while self.__flagthread and count < 50:
                    time.sleep(delay)
                    count += 2
                    # print "%s: %s" % time.ctime(time.time())
                    draw_picture()
                # print('Thread Not ready!')
                time.sleep(2)

        def addNewstock():
            """
            ����һ֧�¹�Ʊ��addnewstock����Ӧ����
            :return:
            """
            stockname = stock.get()
            stocknum = int(num.get())
            stockprice = int(price.get())
            stk = Stock()
            stk.addNewstock(stockname, stockprice, stocknum)

            draw_picture()

        def trade():
            """
            ���ٹ�Ʊ��ʾ���棬����trade��ť����Ӧ����
            :return:
            ##"""
            if not self.__flagexchange:
                self.__flagexchange = True
                self.exchange()

        def deleteStock():
            """
            ɾ��һ֧�¹�Ʊ��deleteStock����Ӧ����
            :return:
            """
            stockname = stock.get()
            stk = Stock()
            stk.deleteStock(stockname)
            draw_picture()

        """
        �ɼ۽������
        """

        canvas = FigureCanvasTkAgg(f, root)
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=4, rowspan=6, sticky=W + N)

        L1 = Label(root, text="Stock Name", font=("Arial", 12), width=10, height=1)
        L1.grid(row=0, column=5, sticky=E)
        stock = Entry(root)
        stock.grid(row=0, column=6, sticky=E)

        L2 = Label(root, text="Stock Num", font=("Arial", 12), width=10, height=1)
        L2.grid(row=1, column=5, sticky=W)
        num = Entry(root)
        num.grid(row=1, column=6, sticky=E)

        L3 = Label(root, text="Stock Price", font=("Arial", 12), width=10, height=1)
        L3.grid(row=2, column=5, sticky=W)
        price = Entry(root)
        price.grid(row=2, column=6, sticky=E)

        #  ����Աӵ����ɾ��Ʊ�Ĺ���
        if self.__flagadmin :
            Button(root, text="AddStock", command=addNewstock, bg="grey", width=10, height=1).grid(row=3, column=5,
                                                                                                   sticky=W)
            Button(root, text="DelStock", command=deleteStock, bg="grey", width=10, height=1).grid(row=3, column=6,
                                                                                               sticky=W)

        Button(root, text="RefStock", command=draw_picture, bg="grey", width=10, height=1).grid(row=4, column=5,
                                                                                                sticky=W)
        Button(root, text="Go2Trade", command=trade, bg="grey", width=10, height=1).grid(row=4, column=6, sticky=W)
        Button(root, text="QuitStock", command=quit, bg="grey", width=10, height=1).grid(row=5, column=5, sticky=W)

        draw_picture()
        mainloop()

    def exchange(self):
        """
        �û���Ϣ��������ʾ����
        :return:
        """
        root = Tk()
        root.resizable(width=True, height=True)
        root.wm_title("StockExchange       current user : " + self.__username)
        f = Figure(figsize=(5, 5), dpi=100)

        # ��ͼͼ�ꡢͼ����ʾ�������
        def check():
            """
            ͼ��button��ʾ�������
            :return:
            """
            user = User(self.__username)

            '''�û����й�Ʊ'''
            str1 = user.getStockholdingMsg()
            userStock.delete('1.0', END)
            userStock.selection_clear()
            userStock.insert(END, str1)
            '''�û��ֽ����'''
            userCurrency.delete(0, END)
            str2 = user.getBalance()
            userCurrency.insert(0, str2)
            '''�û��ʲ�ӯ��'''
            userGain.delete(0, END)
            str3 = user.getProfitOrLoss()
            userGain.insert(0, str3)
            '''�û����ʲ�'''
            userallProp.delete(0, END)
            str4 = user.getTotalProperty()
            userallProp.insert(0, str4)
            '''�û���Ʊ���ʲ�'''
            userStockPro.selection_clear()
            str5 = str(round(user.getStockProp(), 2))
            userStockPro.delete(0, END)
            userStockPro.insert(0, str5)

            draw_picture()

        def __init():
            """
            ��λ
            :return:
            """
            stk = Stock()
            stk.initStock()
            check()

            # �˳�����

        def quit():
            """
            �˳��������˳����桢����,quit��ť��Ӧ����
            :return:
            """
            root.quit()
            root.destroy()
            self.__flagexchange = False

        def back():
            """
            ���غ������رյ�ǰ���棬�ص��ɼ۽��棬back��ť��Ӧ����
            :return:
            """
            if not self.__flagshowstock:
                self.__flagshowstock = True
                self.showStock()

        # ��ͼ����
        def draw_picture():
            """
            �����û���Ʊ����ͼ��
            :return:
            """
            user = User(self.__username)
            user.drawUserExchange(f)
            canvas.draw()

        def sell():
            """
            �����Ʊ��sell��ť��Ӧ����
            :return:
            """
            stockname = exchangeStockname.get()
            stocknum = int(exchangeStocknum.get())
            user = User(self.__username)
            user.sellOneStock(stockname, -stocknum)
            check()

        def buy():
            """
            �����Ʊ��buy��ť��Ӧ����
            :return:
            """
            stockname = exchangeStockname.get()
            stocknum = int(exchangeStocknum.get())
            # �ں���֮�л�ò���������û�м��ذ�ť��ֱ�ӻ�ȡ���õ����ǿ���
            user = User(self.__username)
            user.buyOneStock(stockname, stocknum)
            check()

        """
        �ɼ۽������
        """

        canvas = FigureCanvasTkAgg(f, root)
        canvas.get_tk_widget().grid(row=0, column=1, columnspan=5, rowspan=5, sticky=W + N)

        L1 = Label(root, text="���׹�Ʊ����", font=("Arial", 11))
        L1.grid(row=0, column=6, sticky=W)
        exchangeStockname = Entry(root)
        exchangeStockname.grid(row=0, column=7, sticky=W, padx=2)

        L2 = Label(root, text="���׹�Ʊ��Ŀ", font=("Arial", 11))
        L2.grid(row=0, column=8, sticky=W, padx=2)
        exchangeStocknum = Entry(root)
        exchangeStocknum.grid(row=0, column=9, sticky=W)

        L3 = Label(root, text="�û���Ʊ���ʲ�", font=("Arial", 11))
        L3.grid(row=0, column=10, sticky=W, padx=2)
        userStockPro = Entry(root)
        userStockPro.grid(row=0, column=11, sticky=W)

        L4 = Label(root, text="�û���ǰ���ʲ�", font=("Arial", 11))
        L4.grid(row=1, column=6, sticky=W, padx=2)
        userallProp = Entry(root)
        userallProp.grid(row=1, column=7, sticky=W)

        L5 = Label(root, text="�û���ǰ�ֽ���", font=("Arial", 11))
        L5.grid(row=1, column=8, sticky=W, padx=2)
        userCurrency = Entry(root)
        userCurrency.grid(row=1, column=9, sticky=W)

        L6 = Label(root, text="�û���ǰӯ����", font=("Arial", 11))
        L6.grid(row=1, column=10, sticky=W, padx=2)
        userGain = Entry(root)
        userGain.grid(row=1, column=11, sticky=W)

        L7 = Label(root, text="�û���Ʊ���й�Ʊ", font=("Arial", 11))
        L7.grid(row=3, column=6, sticky=W)
        userStock = Text(root)
        userStock.grid(row=3, column=7, columnspan=10, sticky=W)

        Button(root, text="�����û���Ϣ", command=check, bg="grey", width=8, height=1, font=("Arial", 11)).grid(row=2,
                                                                                                            column=6)
        Button(root, text="SellStock", command=sell, bg="grey", width=8, height=1, font=("Arial", 11)).grid(row=2,
                                                                                                            column=7)
        Button(root, text="��ʼ���û���Ʊ", command=__init, bg="grey", width=8, height=1, font=("Arial", 11)).grid(row=2,
                                                                                                              column=11)
        Button(root, text="BuyStocks", command=buy, bg="grey", width=8, height=1, font=("Arial", 11)).grid(row=2,
                                                                                                           column=8)
        Button(root, text="�˳����׽���", command=quit, bg="grey", width=8, height=1, font=("Arial", 11)).grid(row=2,
                                                                                                            column=9)
        Button(root, text="���ع��н���", command=back, bg="grey", width=8, height=1, font=("Arial", 11)).grid(row=2, column=10)

        check()
        mainloop()


def threadtest(viewframe):
    thread.start_new_thread(viewframe.showStock().autodraw_picture, (1, 3))


if __name__ == '__main__':
    """
    ������
    """
    window = ViewFrame()
    # threadtest(window)
    window.loginSys()
