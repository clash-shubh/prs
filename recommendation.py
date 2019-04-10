


class Recommendation():


    def recommend(i1,i2,i3,i4):
        import pandas as pd
        dataset=pd.read_csv('static/train.csv')
        dataset

        x= dataset[['input 1','input 2','input 3','input 4']]
        y=dataset['output']
        from sklearn.model_selection import train_test_split
        x_train, x_test , y_train , y_test = train_test_split(x,y,test_size=0.2)

        from sklearn.linear_model import LinearRegression
        regressor = LinearRegression()
        regressor.fit(x,y)

        y_pred = regressor.predict([[i1,i2,i3,i4]])


        return tuple(y_pred)
