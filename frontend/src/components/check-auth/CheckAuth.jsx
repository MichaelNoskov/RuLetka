import Cookies from 'js-cookie';

import { useNavigate } from "react-router"
import { appRoutes } from "../../const"
import { useEffect } from "react"

const CheckAuth = function({children}){
    const token = Cookies.get('access_token');
    const navigate = useNavigate()

    useEffect(()=>{
        if (token === undefined) {
            console.log('unauthorized')
            navigate(appRoutes.login)
        }
    }, [navigate, token])

    if (token) {console.log(`login successful! token: ${token}`)}

    return children
}

export default CheckAuth