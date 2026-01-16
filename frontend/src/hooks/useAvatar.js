import { useState, useEffect, useCallback, useRef } from 'react';
import { URLs } from '../const';

export const useAvatar = () => {
    const [avatarUrl, setAvatarUrl] = useState('');
    const [avatarLoading, setAvatarLoading] = useState(false);
    const [avatarError, setAvatarError] = useState(false);
    const isInitialLoad = useRef(true);
    const currentAvatarUrlRef = useRef('');

    const fetchAvatar = useCallback(async () => {
        try {
            setAvatarLoading(true);
            setAvatarError(false);
            
            const response = await fetch(`${URLs.backendHost}/api/profile/image`, {
                method: 'GET',
                credentials: 'include',
            });
            
            if (currentAvatarUrlRef.current && currentAvatarUrlRef.current.startsWith('blob:')) {
                URL.revokeObjectURL(currentAvatarUrlRef.current);
            }

            if (response.ok) {
                const blob = await response.blob();
                const newUrl = URL.createObjectURL(blob);
                currentAvatarUrlRef.current = newUrl;
                setAvatarUrl(newUrl);
                console.log('✅ Аватар загружен');
            } else {
                setAvatarUrl('');
                currentAvatarUrlRef.current = '';
            }
        } catch (error) {
            console.log('ℹ️ Нет аватара:', error);
            setAvatarUrl('');
            currentAvatarUrlRef.current = '';
            setAvatarError(true);
        } finally {
            setAvatarLoading(false);
        }
    }, []);

    useEffect(() => {
        if (isInitialLoad.current) {
            isInitialLoad.current = false;
            fetchAvatar();
        }
    }, [fetchAvatar]);

    const uploadAvatar = async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${URLs.backendHost}/api/profile/image`, {
            method: 'POST',
            body: formData,
            credentials: 'include',
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Ошибка загрузки аватара');
        }

        const data = await response.json();
        console.log('✅ Аватар загружен:', data.message);
        
        await fetchAvatar();
        return data.avatar_url;
    };

    const handleAvatarClick = (event, onError = null) => {
        event.stopPropagation();
        
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.style.display = 'none';
        document.body.appendChild(input);
        input.click();
        
        input.onchange = async (e) => {
            const file = e.target.files?.[0];
            document.body.removeChild(input);
            if (!file) return;
            
            try {
                setAvatarLoading(true);
                await uploadAvatar(file);
            } catch (error) {
                console.error('❌ Ошибка загрузки аватара:', error);
                onError?.(error);
                alert(error.message);
            } finally {
                setAvatarLoading(false);
            }
        };
    };

    useEffect(() => {
        return () => {
            if (currentAvatarUrlRef.current && currentAvatarUrlRef.current.startsWith('blob:')) {
                URL.revokeObjectURL(currentAvatarUrlRef.current);
            }
        };
    }, []);

    return {
        avatarUrl,
        avatarLoading,
        avatarError,
        fetchAvatar,
        uploadAvatar,
        handleAvatarClick
    };
};
