//Этот файл необходим для  мостика между REACT-фронтендом и FastAPI - бэкендом 
import axios from 'axios'; //axios это библиотека для отправки запросов на сервер
//определяем адрес бэкенда, либо переменная окружения, либо адрес разработки
const API_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({//создаем axios 
    baseURL: API_URL,//все запросы будут начинаться с этого адреса
    headers: {
        'Content-Type' : 'application/json',//говорим серверу, что отправляем JSON
    },
});

api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token.trim()}`;
    }
    return config;
});

//получение остатка на дату
export const getBalance = (date) => { //принимает параметр date-определенную дату
    return api.get(`/api/balance/${date}`); //Делает get запрос по адресу /api/balance/2024-01-15
};
//получение транзакций за период
export const getTransactions = (startDate, endDate) => {
    return api.get('/api/transactions', {
        params: {start_date: startDate, end_date: endDate}
    }); //Здесь параметры передаются как query параметры в URL
};
//добавление новой транзакции
export const addTransaction = (data) => {
    return api.post('/api/transactions', data);
}; //метод POST для создания новго ресурса. Вторым параметром передадим данные(тело запроса)

//Получение категорий
export const getCategories = () => {
    return api.get('/api/categories');
};

export const register = (data) => {
    return api.post('/api/auth/register', data);
};

export const login = (formData) => {
    return api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded'}
    });
};

export default api; //экспортируем на случай нестандартных запросов

//Структура запроса: React Component → api.js → axios → HTTP request → FastAPI → Database   