"""Plain-text verification and reset templates (en, pt-BR)."""

from __future__ import annotations

_TEMPLATES: dict[str, dict[str, dict[str, str]]] = {
    'en': {
        'verify': {
            'subject': 'Confirm your email for {app_name}',
            'body': (
                'Confirm your email for {app_name}\n'
                '\n'
                "You're receiving this because someone signed up for {app_name} "
                "with this address. If it wasn't you, ignore this email.\n"
                '\n'
                'Confirm your email:\n'
                '\n'
                '{link}\n'
                '\n'
                'This link expires in 24 hours.\n'
            ),
        },
        'reset': {
            'subject': 'Reset your {app_name} password',
            'body': (
                'Reset your {app_name} password\n'
                '\n'
                "You're receiving this because someone requested a password reset "
                "for {app_name}. If it wasn't you, ignore this email.\n"
                '\n'
                'Reset your password:\n'
                '\n'
                '{link}\n'
                '\n'
                'This link expires in 1 hour.\n'
            ),
        },
    },
    'pt-BR': {
        'verify': {
            'subject': 'Confirme seu e-mail para {app_name}',
            'body': (
                'Confirme seu e-mail para {app_name}\n'
                '\n'
                'Você está recebendo esta mensagem porque alguém se cadastrou no '
                '{app_name} com este endereço. Se não foi você, ignore este e-mail.\n'
                '\n'
                'Confirme seu e-mail:\n'
                '\n'
                '{link}\n'
                '\n'
                'Este link expira em 24 horas.\n'
            ),
        },
        'reset': {
            'subject': 'Redefina sua senha do {app_name}',
            'body': (
                'Redefina sua senha do {app_name}\n'
                '\n'
                'Você está recebendo esta mensagem porque alguém pediu para '
                'redefinir a senha do {app_name}. Se não foi você, ignore '
                'este e-mail.\n'
                '\n'
                'Redefina sua senha:\n'
                '\n'
                '{link}\n'
                '\n'
                'Este link expira em 1 hora.\n'
            ),
        },
    },
}


def render_email(
    purpose: str, locale: str, app_name: str, link: str
) -> tuple[str, str]:
    """Return ``(subject, body)`` for ``purpose`` in ``locale``.

    Args:
        purpose: ``verify`` or ``reset``.
        locale: Whitelisted locale (``en`` or ``pt-BR``).
        app_name: Display name interpolated into subject and body.
        link: Absolute frontend action URL (token already included).

    Returns:
        Subject and plain-text body.
    """
    catalog = _TEMPLATES.get(locale) or _TEMPLATES['en']
    template = catalog.get(purpose) or _TEMPLATES['en'][purpose]
    return (
        template['subject'].format(app_name=app_name),
        template['body'].format(app_name=app_name, link=link),
    )
