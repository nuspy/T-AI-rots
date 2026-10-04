// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'carta.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$LetteraEbraica {

 String get nome; String get glifo; int get valore;
/// Create a copy of LetteraEbraica
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LetteraEbraicaCopyWith<LetteraEbraica> get copyWith => _$LetteraEbraicaCopyWithImpl<LetteraEbraica>(this as LetteraEbraica, _$identity);

  /// Serializes this LetteraEbraica to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as LetteraEbraica;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LetteraEbraica&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.glifo, _this.glifo) || other.glifo == _this.glifo)&&(identical(other.valore, _this.valore) || other.valore == _this.valore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as LetteraEbraica;
  return Object.hash(runtimeType,_this.nome,_this.glifo,_this.valore);
}

@override
String toString() {
  final _this = this as LetteraEbraica;
  return 'LetteraEbraica(nome: ${_this.nome}, glifo: ${_this.glifo}, valore: ${_this.valore})';
}


}

/// @nodoc
abstract mixin class $LetteraEbraicaCopyWith<$Res>  {
  factory $LetteraEbraicaCopyWith(LetteraEbraica value, $Res Function(LetteraEbraica) _then) = _$LetteraEbraicaCopyWithImpl;
@useResult
$Res call({
 String nome, String glifo, int valore
});




}
/// @nodoc
class _$LetteraEbraicaCopyWithImpl<$Res>
    implements $LetteraEbraicaCopyWith<$Res> {
  _$LetteraEbraicaCopyWithImpl(this._self, this._then);

  final LetteraEbraica _self;
  final $Res Function(LetteraEbraica) _then;

/// Create a copy of LetteraEbraica
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? nome = null,Object? glifo = null,Object? valore = null,}) {
  return _then(LetteraEbraica(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,glifo: null == glifo ? _self.glifo : glifo // ignore: cast_nullable_to_non_nullable
as String,valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [LetteraEbraica].
extension LetteraEbraicaPatterns on LetteraEbraica {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LetteraEbraica value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LetteraEbraica() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LetteraEbraica value)  $default,){
final _that = this;
switch (_that) {
case _LetteraEbraica():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LetteraEbraica value)?  $default,){
final _that = this;
switch (_that) {
case _LetteraEbraica() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String nome,  String glifo,  int valore)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LetteraEbraica() when $default != null:
return $default(_that.nome,_that.glifo,_that.valore);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String nome,  String glifo,  int valore)  $default,) {final _that = this;
switch (_that) {
case _LetteraEbraica():
return $default(_that.nome,_that.glifo,_that.valore);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String nome,  String glifo,  int valore)?  $default,) {final _that = this;
switch (_that) {
case _LetteraEbraica() when $default != null:
return $default(_that.nome,_that.glifo,_that.valore);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LetteraEbraica implements LetteraEbraica {
  const _LetteraEbraica({required this.nome, required this.glifo, required this.valore});
  factory _LetteraEbraica.fromJson(Map<String, dynamic> json) => _$LetteraEbraicaFromJson(json);

@override final  String nome;
@override final  String glifo;
@override final  int valore;

/// Create a copy of LetteraEbraica
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LetteraEbraicaCopyWith<_LetteraEbraica> get copyWith => __$LetteraEbraicaCopyWithImpl<_LetteraEbraica>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LetteraEbraicaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _LetteraEbraica&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.glifo, glifo) || other.glifo == glifo)&&(identical(other.valore, valore) || other.valore == valore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,nome,glifo,valore);
}

@override
String toString() {
    return 'LetteraEbraica(nome: $nome, glifo: $glifo, valore: $valore)';
}


}

/// @nodoc
abstract mixin class _$LetteraEbraicaCopyWith<$Res> implements $LetteraEbraicaCopyWith<$Res> {
  factory _$LetteraEbraicaCopyWith(_LetteraEbraica value, $Res Function(_LetteraEbraica) _then) = __$LetteraEbraicaCopyWithImpl;
@override @useResult
$Res call({
 String nome, String glifo, int valore
});




}
/// @nodoc
class __$LetteraEbraicaCopyWithImpl<$Res>
    implements _$LetteraEbraicaCopyWith<$Res> {
  __$LetteraEbraicaCopyWithImpl(this._self, this._then);

  final _LetteraEbraica _self;
  final $Res Function(_LetteraEbraica) _then;

/// Create a copy of LetteraEbraica
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? nome = null,Object? glifo = null,Object? valore = null,}) {
  return _then(_LetteraEbraica(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,glifo: null == glifo ? _self.glifo : glifo // ignore: cast_nullable_to_non_nullable
as String,valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$Carta {

 String get id; String get arcano; int? get numero; String? get numeroRomano; String? get seme; String? get rango; String get nomeThoth; String? get titoloThoth; String get nomeIt;/// Il nome nelle altre lingue: `en` sempre, poi quelle con nomi propri.
 Map<String, String> get nomi;/// La lingua dei testi chiesta con `?lang=` (`it` o `en`): `nome` e `slug` sono in quella lingua.
 String? get lang; String? get nome; String? get slug; Map<String, String> get slugs; String? get elementoLabel; String? get semeLabel; String? get rangoLabel; String? get arcanoLabel; LetteraEbraica? get letteraEbraica; String get elemento; String get astrologia; List<String> get paroleChiave; List<String> get colori; int? get percorso; List<String>? get collega; String? get sefira; Map<String, String>? get significati; String? get dritto; String? get rovescio; Map<String, String>? get ambiti; String? get notaCrowley;
/// Create a copy of Carta
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CartaCopyWith<Carta> get copyWith => _$CartaCopyWithImpl<Carta>(this as Carta, _$identity);

  /// Serializes this Carta to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Carta;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Carta&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.arcano, _this.arcano) || other.arcano == _this.arcano)&&(identical(other.numero, _this.numero) || other.numero == _this.numero)&&(identical(other.numeroRomano, _this.numeroRomano) || other.numeroRomano == _this.numeroRomano)&&(identical(other.seme, _this.seme) || other.seme == _this.seme)&&(identical(other.rango, _this.rango) || other.rango == _this.rango)&&(identical(other.nomeThoth, _this.nomeThoth) || other.nomeThoth == _this.nomeThoth)&&(identical(other.titoloThoth, _this.titoloThoth) || other.titoloThoth == _this.titoloThoth)&&(identical(other.nomeIt, _this.nomeIt) || other.nomeIt == _this.nomeIt)&&const DeepCollectionEquality().equals(other.nomi, _this.nomi)&&(identical(other.lang, _this.lang) || other.lang == _this.lang)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&const DeepCollectionEquality().equals(other.slugs, _this.slugs)&&(identical(other.elementoLabel, _this.elementoLabel) || other.elementoLabel == _this.elementoLabel)&&(identical(other.semeLabel, _this.semeLabel) || other.semeLabel == _this.semeLabel)&&(identical(other.rangoLabel, _this.rangoLabel) || other.rangoLabel == _this.rangoLabel)&&(identical(other.arcanoLabel, _this.arcanoLabel) || other.arcanoLabel == _this.arcanoLabel)&&(identical(other.letteraEbraica, _this.letteraEbraica) || other.letteraEbraica == _this.letteraEbraica)&&(identical(other.elemento, _this.elemento) || other.elemento == _this.elemento)&&(identical(other.astrologia, _this.astrologia) || other.astrologia == _this.astrologia)&&const DeepCollectionEquality().equals(other.paroleChiave, _this.paroleChiave)&&const DeepCollectionEquality().equals(other.colori, _this.colori)&&(identical(other.percorso, _this.percorso) || other.percorso == _this.percorso)&&const DeepCollectionEquality().equals(other.collega, _this.collega)&&(identical(other.sefira, _this.sefira) || other.sefira == _this.sefira)&&const DeepCollectionEquality().equals(other.significati, _this.significati)&&(identical(other.dritto, _this.dritto) || other.dritto == _this.dritto)&&(identical(other.rovescio, _this.rovescio) || other.rovescio == _this.rovescio)&&const DeepCollectionEquality().equals(other.ambiti, _this.ambiti)&&(identical(other.notaCrowley, _this.notaCrowley) || other.notaCrowley == _this.notaCrowley));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Carta;
  return Object.hashAll([runtimeType,_this.id,_this.arcano,_this.numero,_this.numeroRomano,_this.seme,_this.rango,_this.nomeThoth,_this.titoloThoth,_this.nomeIt,const DeepCollectionEquality().hash(_this.nomi),_this.lang,_this.nome,_this.slug,const DeepCollectionEquality().hash(_this.slugs),_this.elementoLabel,_this.semeLabel,_this.rangoLabel,_this.arcanoLabel,_this.letteraEbraica,_this.elemento,_this.astrologia,const DeepCollectionEquality().hash(_this.paroleChiave),const DeepCollectionEquality().hash(_this.colori),_this.percorso,const DeepCollectionEquality().hash(_this.collega),_this.sefira,const DeepCollectionEquality().hash(_this.significati),_this.dritto,_this.rovescio,const DeepCollectionEquality().hash(_this.ambiti),_this.notaCrowley]);
}

@override
String toString() {
  final _this = this as Carta;
  return 'Carta(id: ${_this.id}, arcano: ${_this.arcano}, numero: ${_this.numero}, numeroRomano: ${_this.numeroRomano}, seme: ${_this.seme}, rango: ${_this.rango}, nomeThoth: ${_this.nomeThoth}, titoloThoth: ${_this.titoloThoth}, nomeIt: ${_this.nomeIt}, nomi: ${_this.nomi}, lang: ${_this.lang}, nome: ${_this.nome}, slug: ${_this.slug}, slugs: ${_this.slugs}, elementoLabel: ${_this.elementoLabel}, semeLabel: ${_this.semeLabel}, rangoLabel: ${_this.rangoLabel}, arcanoLabel: ${_this.arcanoLabel}, letteraEbraica: ${_this.letteraEbraica}, elemento: ${_this.elemento}, astrologia: ${_this.astrologia}, paroleChiave: ${_this.paroleChiave}, colori: ${_this.colori}, percorso: ${_this.percorso}, collega: ${_this.collega}, sefira: ${_this.sefira}, significati: ${_this.significati}, dritto: ${_this.dritto}, rovescio: ${_this.rovescio}, ambiti: ${_this.ambiti}, notaCrowley: ${_this.notaCrowley})';
}


}

/// @nodoc
abstract mixin class $CartaCopyWith<$Res>  {
  factory $CartaCopyWith(Carta value, $Res Function(Carta) _then) = _$CartaCopyWithImpl;
@useResult
$Res call({
 String id, String arcano, int? numero, String? numeroRomano, String? seme, String? rango, String nomeThoth, String? titoloThoth, String nomeIt, Map<String, String> nomi, String? lang, String? nome, String? slug, Map<String, String> slugs, String? elementoLabel, String? semeLabel, String? rangoLabel, String? arcanoLabel, LetteraEbraica? letteraEbraica, String elemento, String astrologia, List<String> paroleChiave, List<String> colori, int? percorso, List<String>? collega, String? sefira, Map<String, String>? significati, String? dritto, String? rovescio, Map<String, String>? ambiti, String? notaCrowley
});


$LetteraEbraicaCopyWith<$Res>? get letteraEbraica;

}
/// @nodoc
class _$CartaCopyWithImpl<$Res>
    implements $CartaCopyWith<$Res> {
  _$CartaCopyWithImpl(this._self, this._then);

  final Carta _self;
  final $Res Function(Carta) _then;

/// Create a copy of Carta
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? arcano = null,Object? numero = freezed,Object? numeroRomano = freezed,Object? seme = freezed,Object? rango = freezed,Object? nomeThoth = null,Object? titoloThoth = freezed,Object? nomeIt = null,Object? nomi = null,Object? lang = freezed,Object? nome = freezed,Object? slug = freezed,Object? slugs = null,Object? elementoLabel = freezed,Object? semeLabel = freezed,Object? rangoLabel = freezed,Object? arcanoLabel = freezed,Object? letteraEbraica = freezed,Object? elemento = null,Object? astrologia = null,Object? paroleChiave = null,Object? colori = null,Object? percorso = freezed,Object? collega = freezed,Object? sefira = freezed,Object? significati = freezed,Object? dritto = freezed,Object? rovescio = freezed,Object? ambiti = freezed,Object? notaCrowley = freezed,}) {
  return _then(Carta(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,arcano: null == arcano ? _self.arcano : arcano // ignore: cast_nullable_to_non_nullable
as String,numero: freezed == numero ? _self.numero : numero // ignore: cast_nullable_to_non_nullable
as int?,numeroRomano: freezed == numeroRomano ? _self.numeroRomano : numeroRomano // ignore: cast_nullable_to_non_nullable
as String?,seme: freezed == seme ? _self.seme : seme // ignore: cast_nullable_to_non_nullable
as String?,rango: freezed == rango ? _self.rango : rango // ignore: cast_nullable_to_non_nullable
as String?,nomeThoth: null == nomeThoth ? _self.nomeThoth : nomeThoth // ignore: cast_nullable_to_non_nullable
as String,titoloThoth: freezed == titoloThoth ? _self.titoloThoth : titoloThoth // ignore: cast_nullable_to_non_nullable
as String?,nomeIt: null == nomeIt ? _self.nomeIt : nomeIt // ignore: cast_nullable_to_non_nullable
as String,nomi: null == nomi ? _self.nomi : nomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,nome: freezed == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String?,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,slugs: null == slugs ? _self.slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,elementoLabel: freezed == elementoLabel ? _self.elementoLabel : elementoLabel // ignore: cast_nullable_to_non_nullable
as String?,semeLabel: freezed == semeLabel ? _self.semeLabel : semeLabel // ignore: cast_nullable_to_non_nullable
as String?,rangoLabel: freezed == rangoLabel ? _self.rangoLabel : rangoLabel // ignore: cast_nullable_to_non_nullable
as String?,arcanoLabel: freezed == arcanoLabel ? _self.arcanoLabel : arcanoLabel // ignore: cast_nullable_to_non_nullable
as String?,letteraEbraica: freezed == letteraEbraica ? _self.letteraEbraica : letteraEbraica // ignore: cast_nullable_to_non_nullable
as LetteraEbraica?,elemento: null == elemento ? _self.elemento : elemento // ignore: cast_nullable_to_non_nullable
as String,astrologia: null == astrologia ? _self.astrologia : astrologia // ignore: cast_nullable_to_non_nullable
as String,paroleChiave: null == paroleChiave ? _self.paroleChiave : paroleChiave // ignore: cast_nullable_to_non_nullable
as List<String>,colori: null == colori ? _self.colori : colori // ignore: cast_nullable_to_non_nullable
as List<String>,percorso: freezed == percorso ? _self.percorso : percorso // ignore: cast_nullable_to_non_nullable
as int?,collega: freezed == collega ? _self.collega : collega // ignore: cast_nullable_to_non_nullable
as List<String>?,sefira: freezed == sefira ? _self.sefira : sefira // ignore: cast_nullable_to_non_nullable
as String?,significati: freezed == significati ? _self.significati : significati // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,dritto: freezed == dritto ? _self.dritto : dritto // ignore: cast_nullable_to_non_nullable
as String?,rovescio: freezed == rovescio ? _self.rovescio : rovescio // ignore: cast_nullable_to_non_nullable
as String?,ambiti: freezed == ambiti ? _self.ambiti : ambiti // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,notaCrowley: freezed == notaCrowley ? _self.notaCrowley : notaCrowley // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of Carta
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LetteraEbraicaCopyWith<$Res>? get letteraEbraica {
    if (_self.letteraEbraica == null) {
    return null;
  }

  return $LetteraEbraicaCopyWith<$Res>(_self.letteraEbraica!, (value) {
    return _then(_self.copyWith(letteraEbraica: value));
  });
}
}


/// Adds pattern-matching-related methods to [Carta].
extension CartaPatterns on Carta {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Carta value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Carta() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Carta value)  $default,){
final _that = this;
switch (_that) {
case _Carta():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Carta value)?  $default,){
final _that = this;
switch (_that) {
case _Carta() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String arcano,  int? numero,  String? numeroRomano,  String? seme,  String? rango,  String nomeThoth,  String? titoloThoth,  String nomeIt,  Map<String, String> nomi,  String? lang,  String? nome,  String? slug,  Map<String, String> slugs,  String? elementoLabel,  String? semeLabel,  String? rangoLabel,  String? arcanoLabel,  LetteraEbraica? letteraEbraica,  String elemento,  String astrologia,  List<String> paroleChiave,  List<String> colori,  int? percorso,  List<String>? collega,  String? sefira,  Map<String, String>? significati,  String? dritto,  String? rovescio,  Map<String, String>? ambiti,  String? notaCrowley)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Carta() when $default != null:
return $default(_that.id,_that.arcano,_that.numero,_that.numeroRomano,_that.seme,_that.rango,_that.nomeThoth,_that.titoloThoth,_that.nomeIt,_that.nomi,_that.lang,_that.nome,_that.slug,_that.slugs,_that.elementoLabel,_that.semeLabel,_that.rangoLabel,_that.arcanoLabel,_that.letteraEbraica,_that.elemento,_that.astrologia,_that.paroleChiave,_that.colori,_that.percorso,_that.collega,_that.sefira,_that.significati,_that.dritto,_that.rovescio,_that.ambiti,_that.notaCrowley);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String arcano,  int? numero,  String? numeroRomano,  String? seme,  String? rango,  String nomeThoth,  String? titoloThoth,  String nomeIt,  Map<String, String> nomi,  String? lang,  String? nome,  String? slug,  Map<String, String> slugs,  String? elementoLabel,  String? semeLabel,  String? rangoLabel,  String? arcanoLabel,  LetteraEbraica? letteraEbraica,  String elemento,  String astrologia,  List<String> paroleChiave,  List<String> colori,  int? percorso,  List<String>? collega,  String? sefira,  Map<String, String>? significati,  String? dritto,  String? rovescio,  Map<String, String>? ambiti,  String? notaCrowley)  $default,) {final _that = this;
switch (_that) {
case _Carta():
return $default(_that.id,_that.arcano,_that.numero,_that.numeroRomano,_that.seme,_that.rango,_that.nomeThoth,_that.titoloThoth,_that.nomeIt,_that.nomi,_that.lang,_that.nome,_that.slug,_that.slugs,_that.elementoLabel,_that.semeLabel,_that.rangoLabel,_that.arcanoLabel,_that.letteraEbraica,_that.elemento,_that.astrologia,_that.paroleChiave,_that.colori,_that.percorso,_that.collega,_that.sefira,_that.significati,_that.dritto,_that.rovescio,_that.ambiti,_that.notaCrowley);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String arcano,  int? numero,  String? numeroRomano,  String? seme,  String? rango,  String nomeThoth,  String? titoloThoth,  String nomeIt,  Map<String, String> nomi,  String? lang,  String? nome,  String? slug,  Map<String, String> slugs,  String? elementoLabel,  String? semeLabel,  String? rangoLabel,  String? arcanoLabel,  LetteraEbraica? letteraEbraica,  String elemento,  String astrologia,  List<String> paroleChiave,  List<String> colori,  int? percorso,  List<String>? collega,  String? sefira,  Map<String, String>? significati,  String? dritto,  String? rovescio,  Map<String, String>? ambiti,  String? notaCrowley)?  $default,) {final _that = this;
switch (_that) {
case _Carta() when $default != null:
return $default(_that.id,_that.arcano,_that.numero,_that.numeroRomano,_that.seme,_that.rango,_that.nomeThoth,_that.titoloThoth,_that.nomeIt,_that.nomi,_that.lang,_that.nome,_that.slug,_that.slugs,_that.elementoLabel,_that.semeLabel,_that.rangoLabel,_that.arcanoLabel,_that.letteraEbraica,_that.elemento,_that.astrologia,_that.paroleChiave,_that.colori,_that.percorso,_that.collega,_that.sefira,_that.significati,_that.dritto,_that.rovescio,_that.ambiti,_that.notaCrowley);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Carta extends Carta {
  const _Carta({required this.id, required this.arcano, this.numero, this.numeroRomano, this.seme, this.rango, required this.nomeThoth, this.titoloThoth, required this.nomeIt,  Map<String, String> nomi = const <String, String>{}, this.lang, this.nome, this.slug,  Map<String, String> slugs = const <String, String>{}, this.elementoLabel, this.semeLabel, this.rangoLabel, this.arcanoLabel, this.letteraEbraica, required this.elemento, required this.astrologia,  List<String> paroleChiave = const <String>[],  List<String> colori = const <String>[], this.percorso,  List<String>? collega, this.sefira,  Map<String, String>? significati, this.dritto, this.rovescio,  Map<String, String>? ambiti, this.notaCrowley}): _nomi = nomi,_slugs = slugs,_paroleChiave = paroleChiave,_colori = colori,_collega = collega,_significati = significati,_ambiti = ambiti,super._();
  factory _Carta.fromJson(Map<String, dynamic> json) => _$CartaFromJson(json);

@override final  String id;
@override final  String arcano;
@override final  int? numero;
@override final  String? numeroRomano;
@override final  String? seme;
@override final  String? rango;
@override final  String nomeThoth;
@override final  String? titoloThoth;
@override final  String nomeIt;
/// Il nome nelle altre lingue: `en` sempre, poi quelle con nomi propri.
 final  Map<String, String> _nomi;
/// Il nome nelle altre lingue: `en` sempre, poi quelle con nomi propri.
@override@JsonKey() Map<String, String> get nomi {
  if (_nomi is EqualUnmodifiableMapView) return _nomi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_nomi);
}

/// La lingua dei testi chiesta con `?lang=` (`it` o `en`): `nome` e `slug` sono in quella lingua.
@override final  String? lang;
@override final  String? nome;
@override final  String? slug;
 final  Map<String, String> _slugs;
@override@JsonKey() Map<String, String> get slugs {
  if (_slugs is EqualUnmodifiableMapView) return _slugs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_slugs);
}

@override final  String? elementoLabel;
@override final  String? semeLabel;
@override final  String? rangoLabel;
@override final  String? arcanoLabel;
@override final  LetteraEbraica? letteraEbraica;
@override final  String elemento;
@override final  String astrologia;
 final  List<String> _paroleChiave;
@override@JsonKey() List<String> get paroleChiave {
  if (_paroleChiave is EqualUnmodifiableListView) return _paroleChiave;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_paroleChiave);
}

 final  List<String> _colori;
@override@JsonKey() List<String> get colori {
  if (_colori is EqualUnmodifiableListView) return _colori;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_colori);
}

@override final  int? percorso;
 final  List<String>? _collega;
@override List<String>? get collega {
  final value = _collega;
  if (value == null) return null;
  if (_collega is EqualUnmodifiableListView) return _collega;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override final  String? sefira;
 final  Map<String, String>? _significati;
@override Map<String, String>? get significati {
  final value = _significati;
  if (value == null) return null;
  if (_significati is EqualUnmodifiableMapView) return _significati;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  String? dritto;
@override final  String? rovescio;
 final  Map<String, String>? _ambiti;
@override Map<String, String>? get ambiti {
  final value = _ambiti;
  if (value == null) return null;
  if (_ambiti is EqualUnmodifiableMapView) return _ambiti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  String? notaCrowley;

/// Create a copy of Carta
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CartaCopyWith<_Carta> get copyWith => __$CartaCopyWithImpl<_Carta>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CartaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Carta&&(identical(other.id, id) || other.id == id)&&(identical(other.arcano, arcano) || other.arcano == arcano)&&(identical(other.numero, numero) || other.numero == numero)&&(identical(other.numeroRomano, numeroRomano) || other.numeroRomano == numeroRomano)&&(identical(other.seme, seme) || other.seme == seme)&&(identical(other.rango, rango) || other.rango == rango)&&(identical(other.nomeThoth, nomeThoth) || other.nomeThoth == nomeThoth)&&(identical(other.titoloThoth, titoloThoth) || other.titoloThoth == titoloThoth)&&(identical(other.nomeIt, nomeIt) || other.nomeIt == nomeIt)&&const DeepCollectionEquality().equals(other.nomi, _nomi)&&(identical(other.lang, lang) || other.lang == lang)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.slug, slug) || other.slug == slug)&&const DeepCollectionEquality().equals(other.slugs, _slugs)&&(identical(other.elementoLabel, elementoLabel) || other.elementoLabel == elementoLabel)&&(identical(other.semeLabel, semeLabel) || other.semeLabel == semeLabel)&&(identical(other.rangoLabel, rangoLabel) || other.rangoLabel == rangoLabel)&&(identical(other.arcanoLabel, arcanoLabel) || other.arcanoLabel == arcanoLabel)&&(identical(other.letteraEbraica, letteraEbraica) || other.letteraEbraica == letteraEbraica)&&(identical(other.elemento, elemento) || other.elemento == elemento)&&(identical(other.astrologia, astrologia) || other.astrologia == astrologia)&&const DeepCollectionEquality().equals(other.paroleChiave, _paroleChiave)&&const DeepCollectionEquality().equals(other.colori, _colori)&&(identical(other.percorso, percorso) || other.percorso == percorso)&&const DeepCollectionEquality().equals(other.collega, _collega)&&(identical(other.sefira, sefira) || other.sefira == sefira)&&const DeepCollectionEquality().equals(other.significati, _significati)&&(identical(other.dritto, dritto) || other.dritto == dritto)&&(identical(other.rovescio, rovescio) || other.rovescio == rovescio)&&const DeepCollectionEquality().equals(other.ambiti, _ambiti)&&(identical(other.notaCrowley, notaCrowley) || other.notaCrowley == notaCrowley));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,arcano,numero,numeroRomano,seme,rango,nomeThoth,titoloThoth,nomeIt,const DeepCollectionEquality().hash(_nomi),lang,nome,slug,const DeepCollectionEquality().hash(_slugs),elementoLabel,semeLabel,rangoLabel,arcanoLabel,letteraEbraica,elemento,astrologia,const DeepCollectionEquality().hash(_paroleChiave),const DeepCollectionEquality().hash(_colori),percorso,const DeepCollectionEquality().hash(_collega),sefira,const DeepCollectionEquality().hash(_significati),dritto,rovescio,const DeepCollectionEquality().hash(_ambiti),notaCrowley]);
}

@override
String toString() {
    return 'Carta(id: $id, arcano: $arcano, numero: $numero, numeroRomano: $numeroRomano, seme: $seme, rango: $rango, nomeThoth: $nomeThoth, titoloThoth: $titoloThoth, nomeIt: $nomeIt, nomi: $nomi, lang: $lang, nome: $nome, slug: $slug, slugs: $slugs, elementoLabel: $elementoLabel, semeLabel: $semeLabel, rangoLabel: $rangoLabel, arcanoLabel: $arcanoLabel, letteraEbraica: $letteraEbraica, elemento: $elemento, astrologia: $astrologia, paroleChiave: $paroleChiave, colori: $colori, percorso: $percorso, collega: $collega, sefira: $sefira, significati: $significati, dritto: $dritto, rovescio: $rovescio, ambiti: $ambiti, notaCrowley: $notaCrowley)';
}


}

/// @nodoc
abstract mixin class _$CartaCopyWith<$Res> implements $CartaCopyWith<$Res> {
  factory _$CartaCopyWith(_Carta value, $Res Function(_Carta) _then) = __$CartaCopyWithImpl;
@override @useResult
$Res call({
 String id, String arcano, int? numero, String? numeroRomano, String? seme, String? rango, String nomeThoth, String? titoloThoth, String nomeIt, Map<String, String> nomi, String? lang, String? nome, String? slug, Map<String, String> slugs, String? elementoLabel, String? semeLabel, String? rangoLabel, String? arcanoLabel, LetteraEbraica? letteraEbraica, String elemento, String astrologia, List<String> paroleChiave, List<String> colori, int? percorso, List<String>? collega, String? sefira, Map<String, String>? significati, String? dritto, String? rovescio, Map<String, String>? ambiti, String? notaCrowley
});


@override $LetteraEbraicaCopyWith<$Res>? get letteraEbraica;

}
/// @nodoc
class __$CartaCopyWithImpl<$Res>
    implements _$CartaCopyWith<$Res> {
  __$CartaCopyWithImpl(this._self, this._then);

  final _Carta _self;
  final $Res Function(_Carta) _then;

/// Create a copy of Carta
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? arcano = null,Object? numero = freezed,Object? numeroRomano = freezed,Object? seme = freezed,Object? rango = freezed,Object? nomeThoth = null,Object? titoloThoth = freezed,Object? nomeIt = null,Object? nomi = null,Object? lang = freezed,Object? nome = freezed,Object? slug = freezed,Object? slugs = null,Object? elementoLabel = freezed,Object? semeLabel = freezed,Object? rangoLabel = freezed,Object? arcanoLabel = freezed,Object? letteraEbraica = freezed,Object? elemento = null,Object? astrologia = null,Object? paroleChiave = null,Object? colori = null,Object? percorso = freezed,Object? collega = freezed,Object? sefira = freezed,Object? significati = freezed,Object? dritto = freezed,Object? rovescio = freezed,Object? ambiti = freezed,Object? notaCrowley = freezed,}) {
  return _then(_Carta(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,arcano: null == arcano ? _self.arcano : arcano // ignore: cast_nullable_to_non_nullable
as String,numero: freezed == numero ? _self.numero : numero // ignore: cast_nullable_to_non_nullable
as int?,numeroRomano: freezed == numeroRomano ? _self.numeroRomano : numeroRomano // ignore: cast_nullable_to_non_nullable
as String?,seme: freezed == seme ? _self.seme : seme // ignore: cast_nullable_to_non_nullable
as String?,rango: freezed == rango ? _self.rango : rango // ignore: cast_nullable_to_non_nullable
as String?,nomeThoth: null == nomeThoth ? _self.nomeThoth : nomeThoth // ignore: cast_nullable_to_non_nullable
as String,titoloThoth: freezed == titoloThoth ? _self.titoloThoth : titoloThoth // ignore: cast_nullable_to_non_nullable
as String?,nomeIt: null == nomeIt ? _self.nomeIt : nomeIt // ignore: cast_nullable_to_non_nullable
as String,nomi: null == nomi ? _self._nomi : nomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,nome: freezed == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String?,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,slugs: null == slugs ? _self._slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,elementoLabel: freezed == elementoLabel ? _self.elementoLabel : elementoLabel // ignore: cast_nullable_to_non_nullable
as String?,semeLabel: freezed == semeLabel ? _self.semeLabel : semeLabel // ignore: cast_nullable_to_non_nullable
as String?,rangoLabel: freezed == rangoLabel ? _self.rangoLabel : rangoLabel // ignore: cast_nullable_to_non_nullable
as String?,arcanoLabel: freezed == arcanoLabel ? _self.arcanoLabel : arcanoLabel // ignore: cast_nullable_to_non_nullable
as String?,letteraEbraica: freezed == letteraEbraica ? _self.letteraEbraica : letteraEbraica // ignore: cast_nullable_to_non_nullable
as LetteraEbraica?,elemento: null == elemento ? _self.elemento : elemento // ignore: cast_nullable_to_non_nullable
as String,astrologia: null == astrologia ? _self.astrologia : astrologia // ignore: cast_nullable_to_non_nullable
as String,paroleChiave: null == paroleChiave ? _self._paroleChiave : paroleChiave // ignore: cast_nullable_to_non_nullable
as List<String>,colori: null == colori ? _self._colori : colori // ignore: cast_nullable_to_non_nullable
as List<String>,percorso: freezed == percorso ? _self.percorso : percorso // ignore: cast_nullable_to_non_nullable
as int?,collega: freezed == collega ? _self._collega : collega // ignore: cast_nullable_to_non_nullable
as List<String>?,sefira: freezed == sefira ? _self.sefira : sefira // ignore: cast_nullable_to_non_nullable
as String?,significati: freezed == significati ? _self._significati : significati // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,dritto: freezed == dritto ? _self.dritto : dritto // ignore: cast_nullable_to_non_nullable
as String?,rovescio: freezed == rovescio ? _self.rovescio : rovescio // ignore: cast_nullable_to_non_nullable
as String?,ambiti: freezed == ambiti ? _self._ambiti : ambiti // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,notaCrowley: freezed == notaCrowley ? _self.notaCrowley : notaCrowley // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of Carta
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LetteraEbraicaCopyWith<$Res>? get letteraEbraica {
    if (_self.letteraEbraica == null) {
    return null;
  }

  return $LetteraEbraicaCopyWith<$Res>(_self.letteraEbraica!, (value) {
    return _then(_self.copyWith(letteraEbraica: value));
  });
}
}


/// @nodoc
mixin _$Posizione {

 int get n; String get nome; String get nomeEn; Map<String, String>? get nomi;/// Solo nelle stese speciali: di chi parla (`tu`, `partner`, `coppia`, `strada-a`, `strada-b`).
 String? get soggetto; String get significato; String get domanda; double get x; double get y; double get rotazione; bool get calcolata;
/// Create a copy of Posizione
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PosizioneCopyWith<Posizione> get copyWith => _$PosizioneCopyWithImpl<Posizione>(this as Posizione, _$identity);

  /// Serializes this Posizione to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Posizione;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Posizione&&(identical(other.n, _this.n) || other.n == _this.n)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.nomeEn, _this.nomeEn) || other.nomeEn == _this.nomeEn)&&const DeepCollectionEquality().equals(other.nomi, _this.nomi)&&(identical(other.soggetto, _this.soggetto) || other.soggetto == _this.soggetto)&&(identical(other.significato, _this.significato) || other.significato == _this.significato)&&(identical(other.domanda, _this.domanda) || other.domanda == _this.domanda)&&(identical(other.x, _this.x) || other.x == _this.x)&&(identical(other.y, _this.y) || other.y == _this.y)&&(identical(other.rotazione, _this.rotazione) || other.rotazione == _this.rotazione)&&(identical(other.calcolata, _this.calcolata) || other.calcolata == _this.calcolata));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Posizione;
  return Object.hash(runtimeType,_this.n,_this.nome,_this.nomeEn,const DeepCollectionEquality().hash(_this.nomi),_this.soggetto,_this.significato,_this.domanda,_this.x,_this.y,_this.rotazione,_this.calcolata);
}

@override
String toString() {
  final _this = this as Posizione;
  return 'Posizione(n: ${_this.n}, nome: ${_this.nome}, nomeEn: ${_this.nomeEn}, nomi: ${_this.nomi}, soggetto: ${_this.soggetto}, significato: ${_this.significato}, domanda: ${_this.domanda}, x: ${_this.x}, y: ${_this.y}, rotazione: ${_this.rotazione}, calcolata: ${_this.calcolata})';
}


}

/// @nodoc
abstract mixin class $PosizioneCopyWith<$Res>  {
  factory $PosizioneCopyWith(Posizione value, $Res Function(Posizione) _then) = _$PosizioneCopyWithImpl;
@useResult
$Res call({
 int n, String nome, String nomeEn, Map<String, String>? nomi, String? soggetto, String significato, String domanda, double x, double y, double rotazione, bool calcolata
});




}
/// @nodoc
class _$PosizioneCopyWithImpl<$Res>
    implements $PosizioneCopyWith<$Res> {
  _$PosizioneCopyWithImpl(this._self, this._then);

  final Posizione _self;
  final $Res Function(Posizione) _then;

/// Create a copy of Posizione
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? n = null,Object? nome = null,Object? nomeEn = null,Object? nomi = freezed,Object? soggetto = freezed,Object? significato = null,Object? domanda = null,Object? x = null,Object? y = null,Object? rotazione = null,Object? calcolata = null,}) {
  return _then(Posizione(
n: null == n ? _self.n : n // ignore: cast_nullable_to_non_nullable
as int,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,nomeEn: null == nomeEn ? _self.nomeEn : nomeEn // ignore: cast_nullable_to_non_nullable
as String,nomi: freezed == nomi ? _self.nomi : nomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,soggetto: freezed == soggetto ? _self.soggetto : soggetto // ignore: cast_nullable_to_non_nullable
as String?,significato: null == significato ? _self.significato : significato // ignore: cast_nullable_to_non_nullable
as String,domanda: null == domanda ? _self.domanda : domanda // ignore: cast_nullable_to_non_nullable
as String,x: null == x ? _self.x : x // ignore: cast_nullable_to_non_nullable
as double,y: null == y ? _self.y : y // ignore: cast_nullable_to_non_nullable
as double,rotazione: null == rotazione ? _self.rotazione : rotazione // ignore: cast_nullable_to_non_nullable
as double,calcolata: null == calcolata ? _self.calcolata : calcolata // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [Posizione].
extension PosizionePatterns on Posizione {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Posizione value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Posizione() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Posizione value)  $default,){
final _that = this;
switch (_that) {
case _Posizione():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Posizione value)?  $default,){
final _that = this;
switch (_that) {
case _Posizione() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int n,  String nome,  String nomeEn,  Map<String, String>? nomi,  String? soggetto,  String significato,  String domanda,  double x,  double y,  double rotazione,  bool calcolata)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Posizione() when $default != null:
return $default(_that.n,_that.nome,_that.nomeEn,_that.nomi,_that.soggetto,_that.significato,_that.domanda,_that.x,_that.y,_that.rotazione,_that.calcolata);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int n,  String nome,  String nomeEn,  Map<String, String>? nomi,  String? soggetto,  String significato,  String domanda,  double x,  double y,  double rotazione,  bool calcolata)  $default,) {final _that = this;
switch (_that) {
case _Posizione():
return $default(_that.n,_that.nome,_that.nomeEn,_that.nomi,_that.soggetto,_that.significato,_that.domanda,_that.x,_that.y,_that.rotazione,_that.calcolata);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int n,  String nome,  String nomeEn,  Map<String, String>? nomi,  String? soggetto,  String significato,  String domanda,  double x,  double y,  double rotazione,  bool calcolata)?  $default,) {final _that = this;
switch (_that) {
case _Posizione() when $default != null:
return $default(_that.n,_that.nome,_that.nomeEn,_that.nomi,_that.soggetto,_that.significato,_that.domanda,_that.x,_that.y,_that.rotazione,_that.calcolata);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Posizione implements Posizione {
  const _Posizione({required this.n, required this.nome, required this.nomeEn,  Map<String, String>? nomi, this.soggetto, required this.significato, required this.domanda, required this.x, required this.y, required this.rotazione, required this.calcolata}): _nomi = nomi;
  factory _Posizione.fromJson(Map<String, dynamic> json) => _$PosizioneFromJson(json);

@override final  int n;
@override final  String nome;
@override final  String nomeEn;
 final  Map<String, String>? _nomi;
@override Map<String, String>? get nomi {
  final value = _nomi;
  if (value == null) return null;
  if (_nomi is EqualUnmodifiableMapView) return _nomi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

/// Solo nelle stese speciali: di chi parla (`tu`, `partner`, `coppia`, `strada-a`, `strada-b`).
@override final  String? soggetto;
@override final  String significato;
@override final  String domanda;
@override final  double x;
@override final  double y;
@override final  double rotazione;
@override final  bool calcolata;

/// Create a copy of Posizione
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PosizioneCopyWith<_Posizione> get copyWith => __$PosizioneCopyWithImpl<_Posizione>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PosizioneToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Posizione&&(identical(other.n, n) || other.n == n)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.nomeEn, nomeEn) || other.nomeEn == nomeEn)&&const DeepCollectionEquality().equals(other.nomi, _nomi)&&(identical(other.soggetto, soggetto) || other.soggetto == soggetto)&&(identical(other.significato, significato) || other.significato == significato)&&(identical(other.domanda, domanda) || other.domanda == domanda)&&(identical(other.x, x) || other.x == x)&&(identical(other.y, y) || other.y == y)&&(identical(other.rotazione, rotazione) || other.rotazione == rotazione)&&(identical(other.calcolata, calcolata) || other.calcolata == calcolata));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,n,nome,nomeEn,const DeepCollectionEquality().hash(_nomi),soggetto,significato,domanda,x,y,rotazione,calcolata);
}

@override
String toString() {
    return 'Posizione(n: $n, nome: $nome, nomeEn: $nomeEn, nomi: $nomi, soggetto: $soggetto, significato: $significato, domanda: $domanda, x: $x, y: $y, rotazione: $rotazione, calcolata: $calcolata)';
}


}

/// @nodoc
abstract mixin class _$PosizioneCopyWith<$Res> implements $PosizioneCopyWith<$Res> {
  factory _$PosizioneCopyWith(_Posizione value, $Res Function(_Posizione) _then) = __$PosizioneCopyWithImpl;
@override @useResult
$Res call({
 int n, String nome, String nomeEn, Map<String, String>? nomi, String? soggetto, String significato, String domanda, double x, double y, double rotazione, bool calcolata
});




}
/// @nodoc
class __$PosizioneCopyWithImpl<$Res>
    implements _$PosizioneCopyWith<$Res> {
  __$PosizioneCopyWithImpl(this._self, this._then);

  final _Posizione _self;
  final $Res Function(_Posizione) _then;

/// Create a copy of Posizione
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? n = null,Object? nome = null,Object? nomeEn = null,Object? nomi = freezed,Object? soggetto = freezed,Object? significato = null,Object? domanda = null,Object? x = null,Object? y = null,Object? rotazione = null,Object? calcolata = null,}) {
  return _then(_Posizione(
n: null == n ? _self.n : n // ignore: cast_nullable_to_non_nullable
as int,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,nomeEn: null == nomeEn ? _self.nomeEn : nomeEn // ignore: cast_nullable_to_non_nullable
as String,nomi: freezed == nomi ? _self._nomi : nomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,soggetto: freezed == soggetto ? _self.soggetto : soggetto // ignore: cast_nullable_to_non_nullable
as String?,significato: null == significato ? _self.significato : significato // ignore: cast_nullable_to_non_nullable
as String,domanda: null == domanda ? _self.domanda : domanda // ignore: cast_nullable_to_non_nullable
as String,x: null == x ? _self.x : x // ignore: cast_nullable_to_non_nullable
as double,y: null == y ? _self.y : y // ignore: cast_nullable_to_non_nullable
as double,rotazione: null == rotazione ? _self.rotazione : rotazione // ignore: cast_nullable_to_non_nullable
as double,calcolata: null == calcolata ? _self.calcolata : calcolata // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$Stesa {

 String get id; String get nome; String get nomeEn; Map<String, String>? get nomi; String? get lang; String? get slug; Map<String, String>? get slugs; String? get mazzoLabel; String? get categoriaLabel; String? get stileLabel;/// `standard`, `lavoro`, `compatibilita`, `coppia`.
 String get categoria; List<String>? get temi; String? get stile; double? get larghezza; double? get larghezzaStretto; String get forma; String get mazzo; int get carteDaScegliere; String get origine; String get descrizione; List<Posizione> get posizioni; List<String> get regole;/// Le coppie di posizioni lette insieme: `[a, b, "perché"]`.
 List<List<Object?>> get coppie; bool get sintesiWirth;
/// Create a copy of Stesa
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StesaCopyWith<Stesa> get copyWith => _$StesaCopyWithImpl<Stesa>(this as Stesa, _$identity);

  /// Serializes this Stesa to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Stesa;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Stesa&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.nomeEn, _this.nomeEn) || other.nomeEn == _this.nomeEn)&&const DeepCollectionEquality().equals(other.nomi, _this.nomi)&&(identical(other.lang, _this.lang) || other.lang == _this.lang)&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&const DeepCollectionEquality().equals(other.slugs, _this.slugs)&&(identical(other.mazzoLabel, _this.mazzoLabel) || other.mazzoLabel == _this.mazzoLabel)&&(identical(other.categoriaLabel, _this.categoriaLabel) || other.categoriaLabel == _this.categoriaLabel)&&(identical(other.stileLabel, _this.stileLabel) || other.stileLabel == _this.stileLabel)&&(identical(other.categoria, _this.categoria) || other.categoria == _this.categoria)&&const DeepCollectionEquality().equals(other.temi, _this.temi)&&(identical(other.stile, _this.stile) || other.stile == _this.stile)&&(identical(other.larghezza, _this.larghezza) || other.larghezza == _this.larghezza)&&(identical(other.larghezzaStretto, _this.larghezzaStretto) || other.larghezzaStretto == _this.larghezzaStretto)&&(identical(other.forma, _this.forma) || other.forma == _this.forma)&&(identical(other.mazzo, _this.mazzo) || other.mazzo == _this.mazzo)&&(identical(other.carteDaScegliere, _this.carteDaScegliere) || other.carteDaScegliere == _this.carteDaScegliere)&&(identical(other.origine, _this.origine) || other.origine == _this.origine)&&(identical(other.descrizione, _this.descrizione) || other.descrizione == _this.descrizione)&&const DeepCollectionEquality().equals(other.posizioni, _this.posizioni)&&const DeepCollectionEquality().equals(other.regole, _this.regole)&&const DeepCollectionEquality().equals(other.coppie, _this.coppie)&&(identical(other.sintesiWirth, _this.sintesiWirth) || other.sintesiWirth == _this.sintesiWirth));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Stesa;
  return Object.hashAll([runtimeType,_this.id,_this.nome,_this.nomeEn,const DeepCollectionEquality().hash(_this.nomi),_this.lang,_this.slug,const DeepCollectionEquality().hash(_this.slugs),_this.mazzoLabel,_this.categoriaLabel,_this.stileLabel,_this.categoria,const DeepCollectionEquality().hash(_this.temi),_this.stile,_this.larghezza,_this.larghezzaStretto,_this.forma,_this.mazzo,_this.carteDaScegliere,_this.origine,_this.descrizione,const DeepCollectionEquality().hash(_this.posizioni),const DeepCollectionEquality().hash(_this.regole),const DeepCollectionEquality().hash(_this.coppie),_this.sintesiWirth]);
}

@override
String toString() {
  final _this = this as Stesa;
  return 'Stesa(id: ${_this.id}, nome: ${_this.nome}, nomeEn: ${_this.nomeEn}, nomi: ${_this.nomi}, lang: ${_this.lang}, slug: ${_this.slug}, slugs: ${_this.slugs}, mazzoLabel: ${_this.mazzoLabel}, categoriaLabel: ${_this.categoriaLabel}, stileLabel: ${_this.stileLabel}, categoria: ${_this.categoria}, temi: ${_this.temi}, stile: ${_this.stile}, larghezza: ${_this.larghezza}, larghezzaStretto: ${_this.larghezzaStretto}, forma: ${_this.forma}, mazzo: ${_this.mazzo}, carteDaScegliere: ${_this.carteDaScegliere}, origine: ${_this.origine}, descrizione: ${_this.descrizione}, posizioni: ${_this.posizioni}, regole: ${_this.regole}, coppie: ${_this.coppie}, sintesiWirth: ${_this.sintesiWirth})';
}


}

/// @nodoc
abstract mixin class $StesaCopyWith<$Res>  {
  factory $StesaCopyWith(Stesa value, $Res Function(Stesa) _then) = _$StesaCopyWithImpl;
@useResult
$Res call({
 String id, String nome, String nomeEn, Map<String, String>? nomi, String? lang, String? slug, Map<String, String>? slugs, String? mazzoLabel, String? categoriaLabel, String? stileLabel, String categoria, List<String>? temi, String? stile, double? larghezza, double? larghezzaStretto, String forma, String mazzo, int carteDaScegliere, String origine, String descrizione, List<Posizione> posizioni, List<String> regole, List<List<Object?>> coppie, bool sintesiWirth
});




}
/// @nodoc
class _$StesaCopyWithImpl<$Res>
    implements $StesaCopyWith<$Res> {
  _$StesaCopyWithImpl(this._self, this._then);

  final Stesa _self;
  final $Res Function(Stesa) _then;

/// Create a copy of Stesa
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nome = null,Object? nomeEn = null,Object? nomi = freezed,Object? lang = freezed,Object? slug = freezed,Object? slugs = freezed,Object? mazzoLabel = freezed,Object? categoriaLabel = freezed,Object? stileLabel = freezed,Object? categoria = null,Object? temi = freezed,Object? stile = freezed,Object? larghezza = freezed,Object? larghezzaStretto = freezed,Object? forma = null,Object? mazzo = null,Object? carteDaScegliere = null,Object? origine = null,Object? descrizione = null,Object? posizioni = null,Object? regole = null,Object? coppie = null,Object? sintesiWirth = null,}) {
  return _then(Stesa(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,nomeEn: null == nomeEn ? _self.nomeEn : nomeEn // ignore: cast_nullable_to_non_nullable
as String,nomi: freezed == nomi ? _self.nomi : nomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,slugs: freezed == slugs ? _self.slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,mazzoLabel: freezed == mazzoLabel ? _self.mazzoLabel : mazzoLabel // ignore: cast_nullable_to_non_nullable
as String?,categoriaLabel: freezed == categoriaLabel ? _self.categoriaLabel : categoriaLabel // ignore: cast_nullable_to_non_nullable
as String?,stileLabel: freezed == stileLabel ? _self.stileLabel : stileLabel // ignore: cast_nullable_to_non_nullable
as String?,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,temi: freezed == temi ? _self.temi : temi // ignore: cast_nullable_to_non_nullable
as List<String>?,stile: freezed == stile ? _self.stile : stile // ignore: cast_nullable_to_non_nullable
as String?,larghezza: freezed == larghezza ? _self.larghezza : larghezza // ignore: cast_nullable_to_non_nullable
as double?,larghezzaStretto: freezed == larghezzaStretto ? _self.larghezzaStretto : larghezzaStretto // ignore: cast_nullable_to_non_nullable
as double?,forma: null == forma ? _self.forma : forma // ignore: cast_nullable_to_non_nullable
as String,mazzo: null == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String,carteDaScegliere: null == carteDaScegliere ? _self.carteDaScegliere : carteDaScegliere // ignore: cast_nullable_to_non_nullable
as int,origine: null == origine ? _self.origine : origine // ignore: cast_nullable_to_non_nullable
as String,descrizione: null == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String,posizioni: null == posizioni ? _self.posizioni : posizioni // ignore: cast_nullable_to_non_nullable
as List<Posizione>,regole: null == regole ? _self.regole : regole // ignore: cast_nullable_to_non_nullable
as List<String>,coppie: null == coppie ? _self.coppie : coppie // ignore: cast_nullable_to_non_nullable
as List<List<Object?>>,sintesiWirth: null == sintesiWirth ? _self.sintesiWirth : sintesiWirth // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [Stesa].
extension StesaPatterns on Stesa {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Stesa value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Stesa() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Stesa value)  $default,){
final _that = this;
switch (_that) {
case _Stesa():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Stesa value)?  $default,){
final _that = this;
switch (_that) {
case _Stesa() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String nome,  String nomeEn,  Map<String, String>? nomi,  String? lang,  String? slug,  Map<String, String>? slugs,  String? mazzoLabel,  String? categoriaLabel,  String? stileLabel,  String categoria,  List<String>? temi,  String? stile,  double? larghezza,  double? larghezzaStretto,  String forma,  String mazzo,  int carteDaScegliere,  String origine,  String descrizione,  List<Posizione> posizioni,  List<String> regole,  List<List<Object?>> coppie,  bool sintesiWirth)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Stesa() when $default != null:
return $default(_that.id,_that.nome,_that.nomeEn,_that.nomi,_that.lang,_that.slug,_that.slugs,_that.mazzoLabel,_that.categoriaLabel,_that.stileLabel,_that.categoria,_that.temi,_that.stile,_that.larghezza,_that.larghezzaStretto,_that.forma,_that.mazzo,_that.carteDaScegliere,_that.origine,_that.descrizione,_that.posizioni,_that.regole,_that.coppie,_that.sintesiWirth);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String nome,  String nomeEn,  Map<String, String>? nomi,  String? lang,  String? slug,  Map<String, String>? slugs,  String? mazzoLabel,  String? categoriaLabel,  String? stileLabel,  String categoria,  List<String>? temi,  String? stile,  double? larghezza,  double? larghezzaStretto,  String forma,  String mazzo,  int carteDaScegliere,  String origine,  String descrizione,  List<Posizione> posizioni,  List<String> regole,  List<List<Object?>> coppie,  bool sintesiWirth)  $default,) {final _that = this;
switch (_that) {
case _Stesa():
return $default(_that.id,_that.nome,_that.nomeEn,_that.nomi,_that.lang,_that.slug,_that.slugs,_that.mazzoLabel,_that.categoriaLabel,_that.stileLabel,_that.categoria,_that.temi,_that.stile,_that.larghezza,_that.larghezzaStretto,_that.forma,_that.mazzo,_that.carteDaScegliere,_that.origine,_that.descrizione,_that.posizioni,_that.regole,_that.coppie,_that.sintesiWirth);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String nome,  String nomeEn,  Map<String, String>? nomi,  String? lang,  String? slug,  Map<String, String>? slugs,  String? mazzoLabel,  String? categoriaLabel,  String? stileLabel,  String categoria,  List<String>? temi,  String? stile,  double? larghezza,  double? larghezzaStretto,  String forma,  String mazzo,  int carteDaScegliere,  String origine,  String descrizione,  List<Posizione> posizioni,  List<String> regole,  List<List<Object?>> coppie,  bool sintesiWirth)?  $default,) {final _that = this;
switch (_that) {
case _Stesa() when $default != null:
return $default(_that.id,_that.nome,_that.nomeEn,_that.nomi,_that.lang,_that.slug,_that.slugs,_that.mazzoLabel,_that.categoriaLabel,_that.stileLabel,_that.categoria,_that.temi,_that.stile,_that.larghezza,_that.larghezzaStretto,_that.forma,_that.mazzo,_that.carteDaScegliere,_that.origine,_that.descrizione,_that.posizioni,_that.regole,_that.coppie,_that.sintesiWirth);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Stesa implements Stesa {
  const _Stesa({required this.id, required this.nome, required this.nomeEn,  Map<String, String>? nomi, this.lang, this.slug,  Map<String, String>? slugs, this.mazzoLabel, this.categoriaLabel, this.stileLabel, required this.categoria,  List<String>? temi, this.stile, this.larghezza, this.larghezzaStretto, required this.forma, required this.mazzo, required this.carteDaScegliere, required this.origine, required this.descrizione, required  List<Posizione> posizioni,  List<String> regole = const <String>[],  List<List<Object?>> coppie = const <List<Object?>>[], this.sintesiWirth = false}): _nomi = nomi,_slugs = slugs,_temi = temi,_posizioni = posizioni,_regole = regole,_coppie = coppie;
  factory _Stesa.fromJson(Map<String, dynamic> json) => _$StesaFromJson(json);

@override final  String id;
@override final  String nome;
@override final  String nomeEn;
 final  Map<String, String>? _nomi;
@override Map<String, String>? get nomi {
  final value = _nomi;
  if (value == null) return null;
  if (_nomi is EqualUnmodifiableMapView) return _nomi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  String? lang;
@override final  String? slug;
 final  Map<String, String>? _slugs;
@override Map<String, String>? get slugs {
  final value = _slugs;
  if (value == null) return null;
  if (_slugs is EqualUnmodifiableMapView) return _slugs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  String? mazzoLabel;
@override final  String? categoriaLabel;
@override final  String? stileLabel;
/// `standard`, `lavoro`, `compatibilita`, `coppia`.
@override final  String categoria;
 final  List<String>? _temi;
@override List<String>? get temi {
  final value = _temi;
  if (value == null) return null;
  if (_temi is EqualUnmodifiableListView) return _temi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override final  String? stile;
@override final  double? larghezza;
@override final  double? larghezzaStretto;
@override final  String forma;
@override final  String mazzo;
@override final  int carteDaScegliere;
@override final  String origine;
@override final  String descrizione;
 final  List<Posizione> _posizioni;
@override List<Posizione> get posizioni {
  if (_posizioni is EqualUnmodifiableListView) return _posizioni;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_posizioni);
}

 final  List<String> _regole;
@override@JsonKey() List<String> get regole {
  if (_regole is EqualUnmodifiableListView) return _regole;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_regole);
}

/// Le coppie di posizioni lette insieme: `[a, b, "perché"]`.
 final  List<List<Object?>> _coppie;
/// Le coppie di posizioni lette insieme: `[a, b, "perché"]`.
@override@JsonKey() List<List<Object?>> get coppie {
  if (_coppie is EqualUnmodifiableListView) return _coppie;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_coppie);
}

@override@JsonKey() final  bool sintesiWirth;

/// Create a copy of Stesa
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StesaCopyWith<_Stesa> get copyWith => __$StesaCopyWithImpl<_Stesa>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StesaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Stesa&&(identical(other.id, id) || other.id == id)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.nomeEn, nomeEn) || other.nomeEn == nomeEn)&&const DeepCollectionEquality().equals(other.nomi, _nomi)&&(identical(other.lang, lang) || other.lang == lang)&&(identical(other.slug, slug) || other.slug == slug)&&const DeepCollectionEquality().equals(other.slugs, _slugs)&&(identical(other.mazzoLabel, mazzoLabel) || other.mazzoLabel == mazzoLabel)&&(identical(other.categoriaLabel, categoriaLabel) || other.categoriaLabel == categoriaLabel)&&(identical(other.stileLabel, stileLabel) || other.stileLabel == stileLabel)&&(identical(other.categoria, categoria) || other.categoria == categoria)&&const DeepCollectionEquality().equals(other.temi, _temi)&&(identical(other.stile, stile) || other.stile == stile)&&(identical(other.larghezza, larghezza) || other.larghezza == larghezza)&&(identical(other.larghezzaStretto, larghezzaStretto) || other.larghezzaStretto == larghezzaStretto)&&(identical(other.forma, forma) || other.forma == forma)&&(identical(other.mazzo, mazzo) || other.mazzo == mazzo)&&(identical(other.carteDaScegliere, carteDaScegliere) || other.carteDaScegliere == carteDaScegliere)&&(identical(other.origine, origine) || other.origine == origine)&&(identical(other.descrizione, descrizione) || other.descrizione == descrizione)&&const DeepCollectionEquality().equals(other.posizioni, _posizioni)&&const DeepCollectionEquality().equals(other.regole, _regole)&&const DeepCollectionEquality().equals(other.coppie, _coppie)&&(identical(other.sintesiWirth, sintesiWirth) || other.sintesiWirth == sintesiWirth));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,nome,nomeEn,const DeepCollectionEquality().hash(_nomi),lang,slug,const DeepCollectionEquality().hash(_slugs),mazzoLabel,categoriaLabel,stileLabel,categoria,const DeepCollectionEquality().hash(_temi),stile,larghezza,larghezzaStretto,forma,mazzo,carteDaScegliere,origine,descrizione,const DeepCollectionEquality().hash(_posizioni),const DeepCollectionEquality().hash(_regole),const DeepCollectionEquality().hash(_coppie),sintesiWirth]);
}

@override
String toString() {
    return 'Stesa(id: $id, nome: $nome, nomeEn: $nomeEn, nomi: $nomi, lang: $lang, slug: $slug, slugs: $slugs, mazzoLabel: $mazzoLabel, categoriaLabel: $categoriaLabel, stileLabel: $stileLabel, categoria: $categoria, temi: $temi, stile: $stile, larghezza: $larghezza, larghezzaStretto: $larghezzaStretto, forma: $forma, mazzo: $mazzo, carteDaScegliere: $carteDaScegliere, origine: $origine, descrizione: $descrizione, posizioni: $posizioni, regole: $regole, coppie: $coppie, sintesiWirth: $sintesiWirth)';
}


}

/// @nodoc
abstract mixin class _$StesaCopyWith<$Res> implements $StesaCopyWith<$Res> {
  factory _$StesaCopyWith(_Stesa value, $Res Function(_Stesa) _then) = __$StesaCopyWithImpl;
@override @useResult
$Res call({
 String id, String nome, String nomeEn, Map<String, String>? nomi, String? lang, String? slug, Map<String, String>? slugs, String? mazzoLabel, String? categoriaLabel, String? stileLabel, String categoria, List<String>? temi, String? stile, double? larghezza, double? larghezzaStretto, String forma, String mazzo, int carteDaScegliere, String origine, String descrizione, List<Posizione> posizioni, List<String> regole, List<List<Object?>> coppie, bool sintesiWirth
});




}
/// @nodoc
class __$StesaCopyWithImpl<$Res>
    implements _$StesaCopyWith<$Res> {
  __$StesaCopyWithImpl(this._self, this._then);

  final _Stesa _self;
  final $Res Function(_Stesa) _then;

/// Create a copy of Stesa
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nome = null,Object? nomeEn = null,Object? nomi = freezed,Object? lang = freezed,Object? slug = freezed,Object? slugs = freezed,Object? mazzoLabel = freezed,Object? categoriaLabel = freezed,Object? stileLabel = freezed,Object? categoria = null,Object? temi = freezed,Object? stile = freezed,Object? larghezza = freezed,Object? larghezzaStretto = freezed,Object? forma = null,Object? mazzo = null,Object? carteDaScegliere = null,Object? origine = null,Object? descrizione = null,Object? posizioni = null,Object? regole = null,Object? coppie = null,Object? sintesiWirth = null,}) {
  return _then(_Stesa(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,nomeEn: null == nomeEn ? _self.nomeEn : nomeEn // ignore: cast_nullable_to_non_nullable
as String,nomi: freezed == nomi ? _self._nomi : nomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,slugs: freezed == slugs ? _self._slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,mazzoLabel: freezed == mazzoLabel ? _self.mazzoLabel : mazzoLabel // ignore: cast_nullable_to_non_nullable
as String?,categoriaLabel: freezed == categoriaLabel ? _self.categoriaLabel : categoriaLabel // ignore: cast_nullable_to_non_nullable
as String?,stileLabel: freezed == stileLabel ? _self.stileLabel : stileLabel // ignore: cast_nullable_to_non_nullable
as String?,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,temi: freezed == temi ? _self._temi : temi // ignore: cast_nullable_to_non_nullable
as List<String>?,stile: freezed == stile ? _self.stile : stile // ignore: cast_nullable_to_non_nullable
as String?,larghezza: freezed == larghezza ? _self.larghezza : larghezza // ignore: cast_nullable_to_non_nullable
as double?,larghezzaStretto: freezed == larghezzaStretto ? _self.larghezzaStretto : larghezzaStretto // ignore: cast_nullable_to_non_nullable
as double?,forma: null == forma ? _self.forma : forma // ignore: cast_nullable_to_non_nullable
as String,mazzo: null == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String,carteDaScegliere: null == carteDaScegliere ? _self.carteDaScegliere : carteDaScegliere // ignore: cast_nullable_to_non_nullable
as int,origine: null == origine ? _self.origine : origine // ignore: cast_nullable_to_non_nullable
as String,descrizione: null == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String,posizioni: null == posizioni ? _self._posizioni : posizioni // ignore: cast_nullable_to_non_nullable
as List<Posizione>,regole: null == regole ? _self._regole : regole // ignore: cast_nullable_to_non_nullable
as List<String>,coppie: null == coppie ? _self._coppie : coppie // ignore: cast_nullable_to_non_nullable
as List<List<Object?>>,sintesiWirth: null == sintesiWirth ? _self.sintesiWirth : sintesiWirth // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
