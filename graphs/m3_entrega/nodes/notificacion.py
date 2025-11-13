"""
Nodo de Notificación por Email
Subproceso 3.1.2
"""
import logging
from typing import Dict, Any
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import os

logger = logging.getLogger(__name__)


async def enviar_notificacion(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía notificación por correo al cliente con el enlace de acceso al curso.
    
    Métrica objetivo: Tiempo de entrega tras pago: inmediato - 5 minutos
    """
    logger.info(f"[NOTIFICACIÓN] Preparando email para curso {state.get('curso_id')}")
    
    try:
        # Datos necesarios del estado
        cliente_email = state.get("cliente_email", "cliente@example.com")
        url_acceso = state.get("url_acceso", "")
        curso_titulo = state.get("syllabus_aprobado", {}).get("titulo", "Su Curso")
        lms_course_id = state.get("lms_course_id", "")
        
        # Generar contenido del email
        email_html = _generar_email_bienvenida(
            curso_titulo=curso_titulo,
            url_acceso=url_acceso,
            lms_course_id=lms_course_id
        )
        
        # Enviar email
        email_result = await _enviar_email(
            destinatario=cliente_email,
            asunto=f"✓ Su curso '{curso_titulo}' está listo",
            contenido_html=email_html
        )
        
        if email_result["success"]:
            state["notificacion_enviada"] = True
            state["email_status"] = {
                "sent_at": datetime.utcnow().isoformat(),
                "recipient": cliente_email,
                "status": "delivered"
            }
            logger.info(f"[NOTIFICACIÓN] ✓ Email enviado exitosamente a {cliente_email}")
        else:
            state["notificacion_enviada"] = False
            state["errors"] = state.get("errors", [])
            state["errors"].append(f"Error al enviar email: {email_result.get('error')}")
            logger.error(f"[NOTIFICACIÓN] ✗ Fallo en envío: {email_result.get('error')}")
            
    except Exception as e:
        logger.error(f"[NOTIFICACIÓN] ✗ Excepción: {str(e)}")
        state["notificacion_enviada"] = False
        state["errors"] = state.get("errors", [])
        state["errors"].append(f"Excepción en notificación: {str(e)}")
    
    return state


def _generar_email_bienvenida(curso_titulo: str, url_acceso: str, lms_course_id: str) -> str:
    """Genera el HTML del email de bienvenida"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
            .button {{ display: inline-block; background: #667eea; color: white; 
                      padding: 15px 30px; text-decoration: none; border-radius: 5px; 
                      margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>¡Su curso está listo! 🎓</h1>
            </div>
            <div class="content">
                <h2>Hola,</h2>
                <p>Nos complace informarle que su curso <strong>"{curso_titulo}"</strong> 
                   ha sido publicado exitosamente en nuestra plataforma.</p>
                
                <p><strong>ID del Curso:</strong> {lms_course_id}</p>
                
                <p>Ya puede acceder y comenzar a asignar el curso a sus empleados:</p>
                
                <a href="{url_acceso}" class="button">Acceder al Curso</a>
                
                <h3>Próximos pasos:</h3>
                <ol>
                    <li>Acceda al curso usando el enlace anterior</li>
                    <li>Asigne el curso a los empleados deseados</li>
                    <li>Monitoree el progreso desde el dashboard</li>
                </ol>
                
                <p>Si tiene alguna pregunta, no dude en contactarnos.</p>
                
                <p>¡Feliz aprendizaje!</p>
            </div>
            <div class="footer">
                <p>Centro de Capacitación Ultra-Automatizado</p>
                <p>Este es un correo automático, por favor no responder.</p>
            </div>
        </div>
    </body>
    </html>
    """


async def _enviar_email(destinatario: str, asunto: str, contenido_html: str) -> Dict[str, Any]:
    """
    Envía un email usando SMTP.
    
    En producción, usa las variables de entorno configuradas.
    """
    try:
        # Configuración desde .env
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        email_from = os.getenv("EMAIL_FROM", "noreply@ultraautomatizado.com")
        
        # Crear mensaje
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = asunto
        mensaje["From"] = email_from
        mensaje["To"] = destinatario
        
        # Adjuntar HTML
        parte_html = MIMEText(contenido_html, "html", "utf-8")
        mensaje.attach(parte_html)
        
        # Simulación para desarrollo (comentar en producción)
        logger.info(f"[EMAIL-SIM] Email preparado para {destinatario}")
        logger.info(f"[EMAIL-SIM] Asunto: {asunto}")
        return {
            "success": True,
            "message_id": f"sim-{datetime.utcnow().timestamp()}",
            "sent_at": datetime.utcnow().isoformat()
        }
        
        # Código real para producción (descomentar cuando esté listo):
        """
        await aiosmtplib.send(
            mensaje,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_pass,
            use_tls=True
        )
        
        return {
            "success": True,
            "sent_at": datetime.utcnow().isoformat()
        }
        """
        
    except Exception as e:
        logger.error(f"[EMAIL] Error al enviar: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }