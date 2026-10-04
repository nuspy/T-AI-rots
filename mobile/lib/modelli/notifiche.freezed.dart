// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'notifiche.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$DispositivoNotifica {

 int get id;/// `fcm` (le app) o `webpush` (il sito).
 String get canale;/// `android`, `ios` o `web`.
 String get piattaforma; bool get attivo; String? get lingua; String? get versioneApp;
/// Create a copy of DispositivoNotifica
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DispositivoNotificaCopyWith<DispositivoNotifica> get copyWith => _$DispositivoNotificaCopyWithImpl<DispositivoNotifica>(this as DispositivoNotifica, _$identity);

  /// Serializes this DispositivoNotifica to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as DispositivoNotifica;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DispositivoNotifica&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.canale, _this.canale) || other.canale == _this.canale)&&(identical(other.piattaforma, _this.piattaforma) || other.piattaforma == _this.piattaforma)&&(identical(other.attivo, _this.attivo) || other.attivo == _this.attivo)&&(identical(other.lingua, _this.lingua) || other.lingua == _this.lingua)&&(identical(other.versioneApp, _this.versioneApp) || other.versioneApp == _this.versioneApp));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as DispositivoNotifica;
  return Object.hash(runtimeType,_this.id,_this.canale,_this.piattaforma,_this.attivo,_this.lingua,_this.versioneApp);
}

@override
String toString() {
  final _this = this as DispositivoNotifica;
  return 'DispositivoNotifica(id: ${_this.id}, canale: ${_this.canale}, piattaforma: ${_this.piattaforma}, attivo: ${_this.attivo}, lingua: ${_this.lingua}, versioneApp: ${_this.versioneApp})';
}


}

/// @nodoc
abstract mixin class $DispositivoNotificaCopyWith<$Res>  {
  factory $DispositivoNotificaCopyWith(DispositivoNotifica value, $Res Function(DispositivoNotifica) _then) = _$DispositivoNotificaCopyWithImpl;
@useResult
$Res call({
 int id, String canale, String piattaforma, bool attivo, String? lingua, String? versioneApp
});




}
/// @nodoc
class _$DispositivoNotificaCopyWithImpl<$Res>
    implements $DispositivoNotificaCopyWith<$Res> {
  _$DispositivoNotificaCopyWithImpl(this._self, this._then);

  final DispositivoNotifica _self;
  final $Res Function(DispositivoNotifica) _then;

/// Create a copy of DispositivoNotifica
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? canale = null,Object? piattaforma = null,Object? attivo = null,Object? lingua = freezed,Object? versioneApp = freezed,}) {
  return _then(DispositivoNotifica(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,canale: null == canale ? _self.canale : canale // ignore: cast_nullable_to_non_nullable
as String,piattaforma: null == piattaforma ? _self.piattaforma : piattaforma // ignore: cast_nullable_to_non_nullable
as String,attivo: null == attivo ? _self.attivo : attivo // ignore: cast_nullable_to_non_nullable
as bool,lingua: freezed == lingua ? _self.lingua : lingua // ignore: cast_nullable_to_non_nullable
as String?,versioneApp: freezed == versioneApp ? _self.versioneApp : versioneApp // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [DispositivoNotifica].
extension DispositivoNotificaPatterns on DispositivoNotifica {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DispositivoNotifica value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DispositivoNotifica() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DispositivoNotifica value)  $default,){
final _that = this;
switch (_that) {
case _DispositivoNotifica():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DispositivoNotifica value)?  $default,){
final _that = this;
switch (_that) {
case _DispositivoNotifica() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String canale,  String piattaforma,  bool attivo,  String? lingua,  String? versioneApp)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DispositivoNotifica() when $default != null:
return $default(_that.id,_that.canale,_that.piattaforma,_that.attivo,_that.lingua,_that.versioneApp);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String canale,  String piattaforma,  bool attivo,  String? lingua,  String? versioneApp)  $default,) {final _that = this;
switch (_that) {
case _DispositivoNotifica():
return $default(_that.id,_that.canale,_that.piattaforma,_that.attivo,_that.lingua,_that.versioneApp);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String canale,  String piattaforma,  bool attivo,  String? lingua,  String? versioneApp)?  $default,) {final _that = this;
switch (_that) {
case _DispositivoNotifica() when $default != null:
return $default(_that.id,_that.canale,_that.piattaforma,_that.attivo,_that.lingua,_that.versioneApp);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _DispositivoNotifica implements DispositivoNotifica {
  const _DispositivoNotifica({required this.id, required this.canale, required this.piattaforma, this.attivo = true, this.lingua, this.versioneApp});
  factory _DispositivoNotifica.fromJson(Map<String, dynamic> json) => _$DispositivoNotificaFromJson(json);

@override final  int id;
/// `fcm` (le app) o `webpush` (il sito).
@override final  String canale;
/// `android`, `ios` o `web`.
@override final  String piattaforma;
@override@JsonKey() final  bool attivo;
@override final  String? lingua;
@override final  String? versioneApp;

/// Create a copy of DispositivoNotifica
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DispositivoNotificaCopyWith<_DispositivoNotifica> get copyWith => __$DispositivoNotificaCopyWithImpl<_DispositivoNotifica>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DispositivoNotificaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _DispositivoNotifica&&(identical(other.id, id) || other.id == id)&&(identical(other.canale, canale) || other.canale == canale)&&(identical(other.piattaforma, piattaforma) || other.piattaforma == piattaforma)&&(identical(other.attivo, attivo) || other.attivo == attivo)&&(identical(other.lingua, lingua) || other.lingua == lingua)&&(identical(other.versioneApp, versioneApp) || other.versioneApp == versioneApp));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,canale,piattaforma,attivo,lingua,versioneApp);
}

@override
String toString() {
    return 'DispositivoNotifica(id: $id, canale: $canale, piattaforma: $piattaforma, attivo: $attivo, lingua: $lingua, versioneApp: $versioneApp)';
}


}

/// @nodoc
abstract mixin class _$DispositivoNotificaCopyWith<$Res> implements $DispositivoNotificaCopyWith<$Res> {
  factory _$DispositivoNotificaCopyWith(_DispositivoNotifica value, $Res Function(_DispositivoNotifica) _then) = __$DispositivoNotificaCopyWithImpl;
@override @useResult
$Res call({
 int id, String canale, String piattaforma, bool attivo, String? lingua, String? versioneApp
});




}
/// @nodoc
class __$DispositivoNotificaCopyWithImpl<$Res>
    implements _$DispositivoNotificaCopyWith<$Res> {
  __$DispositivoNotificaCopyWithImpl(this._self, this._then);

  final _DispositivoNotifica _self;
  final $Res Function(_DispositivoNotifica) _then;

/// Create a copy of DispositivoNotifica
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? canale = null,Object? piattaforma = null,Object? attivo = null,Object? lingua = freezed,Object? versioneApp = freezed,}) {
  return _then(_DispositivoNotifica(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,canale: null == canale ? _self.canale : canale // ignore: cast_nullable_to_non_nullable
as String,piattaforma: null == piattaforma ? _self.piattaforma : piattaforma // ignore: cast_nullable_to_non_nullable
as String,attivo: null == attivo ? _self.attivo : attivo // ignore: cast_nullable_to_non_nullable
as bool,lingua: freezed == lingua ? _self.lingua : lingua // ignore: cast_nullable_to_non_nullable
as String?,versioneApp: freezed == versioneApp ? _self.versioneApp : versioneApp // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$PreferenzeNotifica {

 bool get cartaGiorno;/// `HH:MM`, all'ora locale.
 String? get oraCarta; bool get silenzio; String? get silenzioDal; String? get silenzioAl; bool get promemoria; int get tettoPromozioniSettimana; int get tettoMassimo;/// Il consenso `marketing` («Promozioni» nella privacy): lo stesso interruttore.
 bool get promozioni; String? get fusoOrario; List<DispositivoNotifica> get dispositivi;
/// Create a copy of PreferenzeNotifica
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PreferenzeNotificaCopyWith<PreferenzeNotifica> get copyWith => _$PreferenzeNotificaCopyWithImpl<PreferenzeNotifica>(this as PreferenzeNotifica, _$identity);

  /// Serializes this PreferenzeNotifica to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PreferenzeNotifica;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PreferenzeNotifica&&(identical(other.cartaGiorno, _this.cartaGiorno) || other.cartaGiorno == _this.cartaGiorno)&&(identical(other.oraCarta, _this.oraCarta) || other.oraCarta == _this.oraCarta)&&(identical(other.silenzio, _this.silenzio) || other.silenzio == _this.silenzio)&&(identical(other.silenzioDal, _this.silenzioDal) || other.silenzioDal == _this.silenzioDal)&&(identical(other.silenzioAl, _this.silenzioAl) || other.silenzioAl == _this.silenzioAl)&&(identical(other.promemoria, _this.promemoria) || other.promemoria == _this.promemoria)&&(identical(other.tettoPromozioniSettimana, _this.tettoPromozioniSettimana) || other.tettoPromozioniSettimana == _this.tettoPromozioniSettimana)&&(identical(other.tettoMassimo, _this.tettoMassimo) || other.tettoMassimo == _this.tettoMassimo)&&(identical(other.promozioni, _this.promozioni) || other.promozioni == _this.promozioni)&&(identical(other.fusoOrario, _this.fusoOrario) || other.fusoOrario == _this.fusoOrario)&&const DeepCollectionEquality().equals(other.dispositivi, _this.dispositivi));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PreferenzeNotifica;
  return Object.hash(runtimeType,_this.cartaGiorno,_this.oraCarta,_this.silenzio,_this.silenzioDal,_this.silenzioAl,_this.promemoria,_this.tettoPromozioniSettimana,_this.tettoMassimo,_this.promozioni,_this.fusoOrario,const DeepCollectionEquality().hash(_this.dispositivi));
}

@override
String toString() {
  final _this = this as PreferenzeNotifica;
  return 'PreferenzeNotifica(cartaGiorno: ${_this.cartaGiorno}, oraCarta: ${_this.oraCarta}, silenzio: ${_this.silenzio}, silenzioDal: ${_this.silenzioDal}, silenzioAl: ${_this.silenzioAl}, promemoria: ${_this.promemoria}, tettoPromozioniSettimana: ${_this.tettoPromozioniSettimana}, tettoMassimo: ${_this.tettoMassimo}, promozioni: ${_this.promozioni}, fusoOrario: ${_this.fusoOrario}, dispositivi: ${_this.dispositivi})';
}


}

/// @nodoc
abstract mixin class $PreferenzeNotificaCopyWith<$Res>  {
  factory $PreferenzeNotificaCopyWith(PreferenzeNotifica value, $Res Function(PreferenzeNotifica) _then) = _$PreferenzeNotificaCopyWithImpl;
@useResult
$Res call({
 bool cartaGiorno, String? oraCarta, bool silenzio, String? silenzioDal, String? silenzioAl, bool promemoria, int tettoPromozioniSettimana, int tettoMassimo, bool promozioni, String? fusoOrario, List<DispositivoNotifica> dispositivi
});




}
/// @nodoc
class _$PreferenzeNotificaCopyWithImpl<$Res>
    implements $PreferenzeNotificaCopyWith<$Res> {
  _$PreferenzeNotificaCopyWithImpl(this._self, this._then);

  final PreferenzeNotifica _self;
  final $Res Function(PreferenzeNotifica) _then;

/// Create a copy of PreferenzeNotifica
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? cartaGiorno = null,Object? oraCarta = freezed,Object? silenzio = null,Object? silenzioDal = freezed,Object? silenzioAl = freezed,Object? promemoria = null,Object? tettoPromozioniSettimana = null,Object? tettoMassimo = null,Object? promozioni = null,Object? fusoOrario = freezed,Object? dispositivi = null,}) {
  return _then(PreferenzeNotifica(
cartaGiorno: null == cartaGiorno ? _self.cartaGiorno : cartaGiorno // ignore: cast_nullable_to_non_nullable
as bool,oraCarta: freezed == oraCarta ? _self.oraCarta : oraCarta // ignore: cast_nullable_to_non_nullable
as String?,silenzio: null == silenzio ? _self.silenzio : silenzio // ignore: cast_nullable_to_non_nullable
as bool,silenzioDal: freezed == silenzioDal ? _self.silenzioDal : silenzioDal // ignore: cast_nullable_to_non_nullable
as String?,silenzioAl: freezed == silenzioAl ? _self.silenzioAl : silenzioAl // ignore: cast_nullable_to_non_nullable
as String?,promemoria: null == promemoria ? _self.promemoria : promemoria // ignore: cast_nullable_to_non_nullable
as bool,tettoPromozioniSettimana: null == tettoPromozioniSettimana ? _self.tettoPromozioniSettimana : tettoPromozioniSettimana // ignore: cast_nullable_to_non_nullable
as int,tettoMassimo: null == tettoMassimo ? _self.tettoMassimo : tettoMassimo // ignore: cast_nullable_to_non_nullable
as int,promozioni: null == promozioni ? _self.promozioni : promozioni // ignore: cast_nullable_to_non_nullable
as bool,fusoOrario: freezed == fusoOrario ? _self.fusoOrario : fusoOrario // ignore: cast_nullable_to_non_nullable
as String?,dispositivi: null == dispositivi ? _self.dispositivi : dispositivi // ignore: cast_nullable_to_non_nullable
as List<DispositivoNotifica>,
  ));
}

}


/// Adds pattern-matching-related methods to [PreferenzeNotifica].
extension PreferenzeNotificaPatterns on PreferenzeNotifica {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PreferenzeNotifica value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PreferenzeNotifica() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PreferenzeNotifica value)  $default,){
final _that = this;
switch (_that) {
case _PreferenzeNotifica():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PreferenzeNotifica value)?  $default,){
final _that = this;
switch (_that) {
case _PreferenzeNotifica() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool cartaGiorno,  String? oraCarta,  bool silenzio,  String? silenzioDal,  String? silenzioAl,  bool promemoria,  int tettoPromozioniSettimana,  int tettoMassimo,  bool promozioni,  String? fusoOrario,  List<DispositivoNotifica> dispositivi)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PreferenzeNotifica() when $default != null:
return $default(_that.cartaGiorno,_that.oraCarta,_that.silenzio,_that.silenzioDal,_that.silenzioAl,_that.promemoria,_that.tettoPromozioniSettimana,_that.tettoMassimo,_that.promozioni,_that.fusoOrario,_that.dispositivi);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool cartaGiorno,  String? oraCarta,  bool silenzio,  String? silenzioDal,  String? silenzioAl,  bool promemoria,  int tettoPromozioniSettimana,  int tettoMassimo,  bool promozioni,  String? fusoOrario,  List<DispositivoNotifica> dispositivi)  $default,) {final _that = this;
switch (_that) {
case _PreferenzeNotifica():
return $default(_that.cartaGiorno,_that.oraCarta,_that.silenzio,_that.silenzioDal,_that.silenzioAl,_that.promemoria,_that.tettoPromozioniSettimana,_that.tettoMassimo,_that.promozioni,_that.fusoOrario,_that.dispositivi);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool cartaGiorno,  String? oraCarta,  bool silenzio,  String? silenzioDal,  String? silenzioAl,  bool promemoria,  int tettoPromozioniSettimana,  int tettoMassimo,  bool promozioni,  String? fusoOrario,  List<DispositivoNotifica> dispositivi)?  $default,) {final _that = this;
switch (_that) {
case _PreferenzeNotifica() when $default != null:
return $default(_that.cartaGiorno,_that.oraCarta,_that.silenzio,_that.silenzioDal,_that.silenzioAl,_that.promemoria,_that.tettoPromozioniSettimana,_that.tettoMassimo,_that.promozioni,_that.fusoOrario,_that.dispositivi);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PreferenzeNotifica implements PreferenzeNotifica {
  const _PreferenzeNotifica({this.cartaGiorno = true, this.oraCarta, this.silenzio = false, this.silenzioDal, this.silenzioAl, this.promemoria = true, this.tettoPromozioniSettimana = 2, this.tettoMassimo = 2, this.promozioni = false, this.fusoOrario,  List<DispositivoNotifica> dispositivi = const <DispositivoNotifica>[]}): _dispositivi = dispositivi;
  factory _PreferenzeNotifica.fromJson(Map<String, dynamic> json) => _$PreferenzeNotificaFromJson(json);

@override@JsonKey() final  bool cartaGiorno;
/// `HH:MM`, all'ora locale.
@override final  String? oraCarta;
@override@JsonKey() final  bool silenzio;
@override final  String? silenzioDal;
@override final  String? silenzioAl;
@override@JsonKey() final  bool promemoria;
@override@JsonKey() final  int tettoPromozioniSettimana;
@override@JsonKey() final  int tettoMassimo;
/// Il consenso `marketing` («Promozioni» nella privacy): lo stesso interruttore.
@override@JsonKey() final  bool promozioni;
@override final  String? fusoOrario;
 final  List<DispositivoNotifica> _dispositivi;
@override@JsonKey() List<DispositivoNotifica> get dispositivi {
  if (_dispositivi is EqualUnmodifiableListView) return _dispositivi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_dispositivi);
}


/// Create a copy of PreferenzeNotifica
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PreferenzeNotificaCopyWith<_PreferenzeNotifica> get copyWith => __$PreferenzeNotificaCopyWithImpl<_PreferenzeNotifica>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PreferenzeNotificaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PreferenzeNotifica&&(identical(other.cartaGiorno, cartaGiorno) || other.cartaGiorno == cartaGiorno)&&(identical(other.oraCarta, oraCarta) || other.oraCarta == oraCarta)&&(identical(other.silenzio, silenzio) || other.silenzio == silenzio)&&(identical(other.silenzioDal, silenzioDal) || other.silenzioDal == silenzioDal)&&(identical(other.silenzioAl, silenzioAl) || other.silenzioAl == silenzioAl)&&(identical(other.promemoria, promemoria) || other.promemoria == promemoria)&&(identical(other.tettoPromozioniSettimana, tettoPromozioniSettimana) || other.tettoPromozioniSettimana == tettoPromozioniSettimana)&&(identical(other.tettoMassimo, tettoMassimo) || other.tettoMassimo == tettoMassimo)&&(identical(other.promozioni, promozioni) || other.promozioni == promozioni)&&(identical(other.fusoOrario, fusoOrario) || other.fusoOrario == fusoOrario)&&const DeepCollectionEquality().equals(other.dispositivi, _dispositivi));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,cartaGiorno,oraCarta,silenzio,silenzioDal,silenzioAl,promemoria,tettoPromozioniSettimana,tettoMassimo,promozioni,fusoOrario,const DeepCollectionEquality().hash(_dispositivi));
}

@override
String toString() {
    return 'PreferenzeNotifica(cartaGiorno: $cartaGiorno, oraCarta: $oraCarta, silenzio: $silenzio, silenzioDal: $silenzioDal, silenzioAl: $silenzioAl, promemoria: $promemoria, tettoPromozioniSettimana: $tettoPromozioniSettimana, tettoMassimo: $tettoMassimo, promozioni: $promozioni, fusoOrario: $fusoOrario, dispositivi: $dispositivi)';
}


}

/// @nodoc
abstract mixin class _$PreferenzeNotificaCopyWith<$Res> implements $PreferenzeNotificaCopyWith<$Res> {
  factory _$PreferenzeNotificaCopyWith(_PreferenzeNotifica value, $Res Function(_PreferenzeNotifica) _then) = __$PreferenzeNotificaCopyWithImpl;
@override @useResult
$Res call({
 bool cartaGiorno, String? oraCarta, bool silenzio, String? silenzioDal, String? silenzioAl, bool promemoria, int tettoPromozioniSettimana, int tettoMassimo, bool promozioni, String? fusoOrario, List<DispositivoNotifica> dispositivi
});




}
/// @nodoc
class __$PreferenzeNotificaCopyWithImpl<$Res>
    implements _$PreferenzeNotificaCopyWith<$Res> {
  __$PreferenzeNotificaCopyWithImpl(this._self, this._then);

  final _PreferenzeNotifica _self;
  final $Res Function(_PreferenzeNotifica) _then;

/// Create a copy of PreferenzeNotifica
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? cartaGiorno = null,Object? oraCarta = freezed,Object? silenzio = null,Object? silenzioDal = freezed,Object? silenzioAl = freezed,Object? promemoria = null,Object? tettoPromozioniSettimana = null,Object? tettoMassimo = null,Object? promozioni = null,Object? fusoOrario = freezed,Object? dispositivi = null,}) {
  return _then(_PreferenzeNotifica(
cartaGiorno: null == cartaGiorno ? _self.cartaGiorno : cartaGiorno // ignore: cast_nullable_to_non_nullable
as bool,oraCarta: freezed == oraCarta ? _self.oraCarta : oraCarta // ignore: cast_nullable_to_non_nullable
as String?,silenzio: null == silenzio ? _self.silenzio : silenzio // ignore: cast_nullable_to_non_nullable
as bool,silenzioDal: freezed == silenzioDal ? _self.silenzioDal : silenzioDal // ignore: cast_nullable_to_non_nullable
as String?,silenzioAl: freezed == silenzioAl ? _self.silenzioAl : silenzioAl // ignore: cast_nullable_to_non_nullable
as String?,promemoria: null == promemoria ? _self.promemoria : promemoria // ignore: cast_nullable_to_non_nullable
as bool,tettoPromozioniSettimana: null == tettoPromozioniSettimana ? _self.tettoPromozioniSettimana : tettoPromozioniSettimana // ignore: cast_nullable_to_non_nullable
as int,tettoMassimo: null == tettoMassimo ? _self.tettoMassimo : tettoMassimo // ignore: cast_nullable_to_non_nullable
as int,promozioni: null == promozioni ? _self.promozioni : promozioni // ignore: cast_nullable_to_non_nullable
as bool,fusoOrario: freezed == fusoOrario ? _self.fusoOrario : fusoOrario // ignore: cast_nullable_to_non_nullable
as String?,dispositivi: null == dispositivi ? _self._dispositivi : dispositivi // ignore: cast_nullable_to_non_nullable
as List<DispositivoNotifica>,
  ));
}


}

// dart format on
