import requests
from django.contrib import messages
from .models import City
from pynotifier import Notification
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CityForm,UserRegister
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate,login,logout
# Create your views here.
from bs4 import BeautifulSoup
from plyer import notification

def dash(request):
    
    url='http://api.openweathermap.org/data/2.5/weather?q={},&appid=b023426aa015d2308a4073e60078ea43&units=metric'

    if request.method=="POST":
        form=CityForm(request.POST)        
        if form.is_valid():
            NCity=form.cleaned_data['name']            
            CCity=City.objects.filter(name=NCity).count()
            if CCity==0:
                res=requests.get(url.format(NCity)).json()                
                if res['cod']==200:
                    form.save()
                    messages.success(request," "+NCity+" Added Successfully...!!!")
                else: 
                    messages.error(request,"City Does Not Exists...!!!")
            else:
                messages.error(request,"City Already Exists...!!!") 

            
    form=CityForm()
    cities=City.objects.all()
    data=[]
    for city in cities:        
        res=requests.get(url.format(city)).json()   
        city_weather={
            'city':city,
            'temperature' : res['main']['temp'],
            'description' : res['weather'][0]['description'],
            'country' : res['sys']['country'],
            'icon' : res['weather'][0]['icon'],
        }
        data.append(city_weather)  
    context={'data' : data,'form':form}
    return render(request,"dash.html",context)

# create an object to ToastNotifier class
# define a function
def getdata(url):
    r = requests.get(url)
    return r.text
    
htmldata = getdata("https://weather.com/en-IN/weather/today/l/fbae48adde7ca1e8902fa6e1cee6eaa64fbefd2a8af9e009cc24dcb9d76726cb")
  
soup = BeautifulSoup(htmldata, 'html.parser')
  
current_temp = soup.find_all("span", class_= "CurrentConditions--tempValue--MHmYY")
temp=(str(current_temp))
a=temp.index(">")
b=temp.rindex("<")
temp=str(temp[(a+1):b])
chances_rain = soup.find_all("div", class_= "CurrentConditions--phraseValue--mZC_p")
perc_rain = str(chances_rain)
a=perc_rain.index(">")
perc_rain=perc_rain[a+7:len(perc_rain)-14]
perc_rain=str(perc_rain)
     
result = "current_temp is" + temp + "  in Kolar" + "\n" + "increasing temperature" + perc_rain
notification.notify(title="Live weather Upate", message=result,timeout=20)


def delete_city(request,CName):
    City.objects.get(name=CName).delete()
    messages.success(request," "+CName+" Removed Successfully...!!!")
    return redirect('/dash')


def user_register(request):

    if request.method=="POST":
        regfmdata=UserRegister(request.POST)
        message={}
        if regfmdata.is_valid():
            regfmdata.save()
            message['msg']="Congratulation, Register Done Successfully. Please Login"
            message['x']=1
            return render(request, 'register_success.html', message)
    
        else:
            message['msg']="Failed to Register User. Please try Again"
            message['x']=0
            return render(request, 'register_success.html', message)
    
    else:
        
        regfm=UserRegister()
        content={}
        content['regfmdata']=regfm
        return render(request,'register.html',content)
    
def user_login(request):
    fmlog=AuthenticationForm()
    content={}
    content['logfmdata']=fmlog
    if request.method=="POST":
        logfmdata=AuthenticationForm(request=request,data=request.POST)
        if logfmdata.is_valid():
            uname=logfmdata.cleaned_data['username']
            upass=logfmdata.cleaned_data['password']
            r=authenticate(username=uname,password=upass)
            if r is not None:
                login(request,r)#start session and store id of logged in user
                return redirect('/dash')
        else:
            content['msg']="Invaild username and Password!!!"
            return render(request,'index.html',content)
    else:
        return render(request,'index.html',content)
    
def user_logout(request): #it destroy session or data stored in session

    logout(request)
    return redirect('/')

