import 'vuetify/styles';
import '@mdi/font/css/materialdesignicons.css';
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

const lightTheme = {
    dark: false,
    colors: {
        primary:    '#2563EB',
        secondary:  '#64748B',
        success:    '#10B981',
        warning:    '#F59E0B',
        error:      '#EF4444',
        info:       '#3B82F6',
        background: '#FFFFFF',
        surface:    '#F8FAFC',
        'on-background': '#0F172A',
        'on-surface':    '#0F172A',
        border:     '#E2E8F0',
    },
};

const darkTheme = {
    dark: true,
    colors: {
        primary:    '#3B82F6',
        secondary:  '#94A3B8',
        success:    '#34D399',
        warning:    '#FBBF24',
        error:      '#F87171',
        info:       '#60A5FA',
        background: '#0F172A',
        surface:    '#1E293B',
        'on-background': '#F1F5F9',
        'on-surface':    '#F1F5F9',
        border:     '#334155',
    },
};

export const vuetify = createVuetify({
    components,
    directives,
    theme: {
        defaultTheme: 'light',
        themes: {
            light: lightTheme,
            dark:  darkTheme,
        },
    },
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: { mdi },
    },
    defaults: {
        // Give every component sensible spacing/appearance defaults
        // so we don't repeat props everywhere.
        VCard: {
            rounded: 'lg',
            elevation: 0,
            border: true,
        },
        VBtn: {
            rounded: 'md',
        },
        VTextField: {
            variant: 'outlined',
            density: 'comfortable',
        },
        VTextarea: {
            variant: 'outlined',
        },
        VSelect: {
            variant: 'outlined',
            density: 'comfortable',
        },
    },
});
