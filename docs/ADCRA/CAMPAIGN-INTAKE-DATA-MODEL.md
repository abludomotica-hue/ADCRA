# ADCRA — Campaign Intake Studio
## Modelo de Datos y Contratos Formales (CAMPAIGN-INTAKE-DATA-MODEL)
**Versión:** 1.0.0 | **Estado:** APROBADA PARA IMPLEMENTACIÓN  
**Sistema:** ADCRA (Autonomous Digital Campaign & Creative Production System)  

---

## 1. Definición de Tipos y Contratos de Datos (TypeScript & JSON Schema)

Todos los componentes de la interfaz, endpoints del backend y agentes de producción operan bajo contratos fuertemente tipados para garantizar cero ambigüedad semántica.

```typescript
// ==========================================================================
// 1. SESIÓN DE INTAKE Y ESTADO GLOBAL DE BORRADOR
// ==========================================================================
export type IntakeStepStatus = 'COMPLETE' | 'READY' | 'NEEDS_REVIEW' | 'MISSING' | 'OPTIONAL';

export interface CampaignIntakeDraft {
  draft_id: string;
  client_mode: 'NEW_CLIENT' | 'EXISTING_CLIENT';
  selected_client_id?: string;
  active_step: number; // 1 a 17
  last_saved_at: string; // ISO-8601
  is_dirty: boolean;
  version: number;
  steps_status: Record<string, IntakeStepStatus>;
  data: CampaignIntakeData;
}

// ==========================================================================
// 2. DATOS DEL CLIENTE Y CONTACTO
// ==========================================================================
export interface ClientProfile {
  client_id: string;
  legal_name?: string;
  brand_name: string;
  industry: string;
  business_type: 'producto' | 'servicio' | 'ecommerce' | 'restaurante' | 'profesional' | 'organizacion' | 'startup' | 'institucion' | 'otro';
  description: string;
  website_url?: string;
  social_channels: {
    instagram?: string;
    tiktok?: string;
    youtube?: string;
    facebook?: string;
    linkedin?: string;
    whatsapp?: string;
  };
  contact: {
    name: string;
    role: string;
    email: string;
    phone?: string;
  };
  web_analysis?: WebAnalysisInference;
}

export interface WebAnalysisInference {
  inferred_at: string;
  value_proposition: string;
  detected_colors: string[]; // HEX
  detected_fonts: string[];
  detected_claims: string[];
  suggested_tone: string[];
  status: 'PENDING_CONFIRMATION' | 'ACCEPTED' | 'REJECTED' | 'MODIFIED';
}

// ==========================================================================
// 3. OBJETIVO Y RESULTADO DESEADO
// ==========================================================================
export type CampaignObjectiveType = 
  | 'AWARENESS' | 'ENGAGEMENT' | 'CONVERSION' | 'LANZAMIENTO' | 'TRAFICO'
  | 'VENTAS' | 'LEADS' | 'COMUNIDAD' | 'RETENCION' | 'EDUCACION'
  | 'EVENTO' | 'TEMPORADA' | 'REMARKETING' | 'BRANDING';

export type DesiredOutcomeType =
  | 'recordar_marca' | 'visitar_sitio' | 'comprar' | 'escribir_whatsapp'
  | 'registrarse' | 'seguir_redes' | 'compartir' | 'comentar'
  | 'visitar_tienda' | 'conocer_producto' | 'otro';

export interface ObjectiveData {
  primary_objective: CampaignObjectiveType;
  secondary_objectives: CampaignObjectiveType[]; // Máximo 3
  desired_outcome: DesiredOutcomeType;
  custom_outcome_note?: string;
}

// ==========================================================================
// 4. AUDIENCIA TRI-PARTITA
// ==========================================================================
export interface AudienceSegment {
  demographics: {
    age_range: [number, number];
    location: string;
    language: string;
    gender?: string;
    occupation?: string;
  };
  psychographics: {
    interests: string[];
    needs: string[];
    desires: string[];
    motivations: string[];
    objections: string[];
  };
  digital_behavior: {
    primary_platforms: string[];
    media_consumption_habits: string[];
  };
  is_ai_suggested: boolean;
}

export interface AudienceData {
  primary_audience: AudienceSegment;
  secondary_audience?: AudienceSegment;
  exploratory_audience?: AudienceSegment;
}

// ==========================================================================
// 5. IDENTIDAD DE MARCA (BRAND IDENTITY STUDIO)
// ==========================================================================
export interface BrandIdentityData {
  brand_name: string;
  claim: string;
  tagline?: string;
  purpose: string;
  values: string[];
  tone_of_voice: string[];
  mandatory_words: string[];
  forbidden_words: string[];
  visual_identity: {
    primary_color_hex: string;
    secondary_color_hex: string;
    accent_color_hex: string;
    color_temperature_target_kelvin: number;
    typography_primary?: string;
    typography_secondary?: string;
    logo_files: string[];
    brand_manual_pdf?: string;
  };
}

// ==========================================================================
// 6. PRODUCTOS Y OFERTA COMERCIAL
// ==========================================================================
export interface ProductItem {
  id: string;
  name: string;
  description: string;
  price?: number;
  currency?: string;
  benefits: string[];
  features: string[];
  differentiators: string[];
  allowed_claims: string[];
  forbidden_claims: string[];
  product_url?: string;
  media_assets_ids: string[];
}

export interface OfferData {
  is_branding_only: boolean;
  offer_title?: string;
  discount_percentage?: number;
  fixed_price?: number;
  start_date?: string;
  end_date?: string;
  terms_conditions?: string;
  stock_limit?: number;
}

// ==========================================================================
// 7. DIRECCIÓN CREATIVA Y EMOCIONES
// ==========================================================================
export type TargetEmotion = 
  | 'confianza' | 'deseo' | 'curiosidad' | 'nostalgia' | 'alegria'
  | 'pertenencia' | 'tranquilidad' | 'energia' | 'inspiracion'
  | 'urgencia' | 'cercania' | 'exclusividad' | 'otro';

export interface CreativeDirectionData {
  target_emotions: TargetEmotion[]; // Máximo 3
  key_takeaway: string; // Qué debe recordar el usuario
  forbidden_concepts: string; // Qué NO debe comunicar jamás
  visual_style: 'cinematic' | 'documentary' | 'commercial' | 'social_native' | 'editorial';
  narrative_arc_preference: 'hook_build_climax' | 'problem_solution' | 'poetic_manifesto' | 'humorous';
}

// ==========================================================================
// 8. AUDIO E INTELIGENCIA MUSICAL
// ==========================================================================
export interface AudioIntakeData {
  file_path?: string;
  filename?: string;
  duration_seconds: number;
  bpm: number;
  meter: string; // "4/4"
  energy_profile: Array<{ timestamp: number; energy: number }>;
  sections: Array<{ name: 'INTRO' | 'VERSE' | 'CHORUS' | 'BRIDGE' | 'OUTRO'; start: number; end: number }>;
  lyrics?: Array<{ index: number; start: number; end: number; line: string; keywords: string[] }>;
  has_commercial_rights: boolean;
}

// ==========================================================================
// 9. ACTIVOS MULTIMEDIA (ASSET INTELLIGENCE)
// ==========================================================================
export interface AssetItem {
  id: string;
  filename: string;
  file_path: string;
  asset_type: 'video' | 'image' | 'logo' | 'audio' | 'font' | 'pdf_manual' | 'reference';
  technical_specs: {
    width?: number;
    height?: number;
    aspect_ratio?: string;
    fps?: number;
    duration_seconds?: number;
    codec?: string;
    size_bytes: number;
    has_alpha?: boolean;
  };
  ai_analysis: {
    detected_objects: string[];
    faces_detected: boolean;
    product_visible: boolean;
    motion_intensity: 'low' | 'medium' | 'high';
    lighting_quality: 'optimal' | 'underexposed' | 'overexposed';
  };
  validation_status: 'READY' | 'WARNING' | 'ERROR' | 'NEEDS_REVIEW';
  status_reasons: string[];
}

// ==========================================================================
// 10. RESTRICCIONES, BRAND SAFETY Y GOBERNANZA
// ==========================================================================
export interface CampaignConstraints {
  forbidden_words: string[];
  forbidden_claims: string[];
  forbidden_visual_elements: string[];
  legal_disclaimers_required: string[];
  music_rights_cleared: boolean;
  image_rights_cleared: boolean;
  industry_regulations?: string[];
}

export interface AutomationConfig {
  mode: 'MANUAL' | 'ASSISTED' | 'AUTONOMOUS' | 'AUTONOMOUS_APPROVALS';
  approval_checkpoints: {
    concept: boolean;
    storyboard: boolean;
    copy: boolean;
    first_render: boolean;
    master: boolean;
    individual_scenes: boolean;
  };
}

// ==========================================================================
// 11. CAMPAIGN READINESS & PRE-FLIGHT DIAGNOSIS
// ==========================================================================
export interface PreflightDiagnosis {
  readiness_percentage: number;
  overall_rating: 'PRODUCTION_READY' | 'WARNINGS_PRESENT' | 'BLOCKED';
  blockers_count: number;
  warnings_count: number;
  missing_optional_count: number;
  checks: Array<{
    id: string;
    title: string;
    category: 'CLIENT' | 'OBJECTIVE' | 'AUDIENCE' | 'BRAND' | 'PRODUCT' | 'AUDIO' | 'VIDEO' | 'COPY' | 'LEGAL' | 'DELIVERY';
    status: 'PASS' | 'WARNING' | 'BLOCKER' | 'OPTIONAL_MISSING';
    message: string;
    suggested_action?: string;
  }>;
}

// ==========================================================================
// 12. CENTRAL CAMPAIGN MANIFEST (FUENTE ÚNICA DE VERDAD)
// ==========================================================================
export interface CampaignManifest {
  campaign_id: string;
  client_id: string;
  campaign_name: string;
  created_at: string;
  updated_at: string;
  status: 'intake' | 'blueprint_ready' | 'producing' | 'qc_audit' | 'approved' | 'delivered';
  objective: ObjectiveData;
  audience: AudienceData;
  brand: BrandIdentityData;
  products: ProductItem[];
  offer: OfferData;
  creative: CreativeDirectionData;
  audio: AudioIntakeData;
  assets: {
    video_clips: AssetItem[];
    brand_logos: AssetItem[];
    reference_files: AssetItem[];
  };
  channels: string[];
  cta: {
    primary: string;
    secondary?: string;
    url?: string;
    whatsapp?: string;
  };
  constraints: CampaignConstraints;
  automation: AutomationConfig;
  preflight_report?: PreflightDiagnosis;
}
```
