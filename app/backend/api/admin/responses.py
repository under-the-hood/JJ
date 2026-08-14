from fastapi import APIRouter, Depends

from app.backend.database.database import session_dep
from app.backend.dependencies.user import check_admin
from app.backend.dependencies.response import check_response
from app.backend.models.user import User
from app.backend.models.response import Response
import app.backend.services.admin.responses as admin_responses


router = APIRouter(prefix="/responses", tags=['Admin | Responses'])

@router.get('')
async def get_responses(session: session_dep, limit: int = 10, offset: int = 0, admin: User = Depends(check_admin)):

    total, responses = await admin_responses.get_responses(session=session, limit=limit, offset=offset, admin=admin)    
    return {"total": total, "responses": responses}


@router.delete('/{response_id}')
async def delete_response(session: session_dep, current_response: Response = Depends(check_response), admin: User = Depends(check_admin)):

    await admin_responses.delete_response(session=session, current_response=current_response, admin=admin)
    return {'message': 'Response was deleted', "response_id": current_response.id}