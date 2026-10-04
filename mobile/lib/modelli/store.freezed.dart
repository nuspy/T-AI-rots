// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'store.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$PianoStore {

 String get slug; String get nome; String? get descrizione;/// `pacchetto` o `abbonamento`.
 String get tipo; int get crediti; Map<String, num> get limiti; int get livello;
/// Create a copy of PianoStore
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PianoStoreCopyWith<PianoStore> get copyWith => _$PianoStoreCopyWithImpl<PianoStore>(this as PianoStore, _$identity);

  /// Serializes this PianoStore to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PianoStore;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PianoStore&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.descrizione, _this.descrizione) || other.descrizione == _this.descrizione)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.crediti, _this.crediti) || other.crediti == _this.crediti)&&const DeepCollectionEquality().equals(other.limiti, _this.limiti)&&(identical(other.livello, _this.livello) || other.livello == _this.livello));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PianoStore;
  return Object.hash(runtimeType,_this.slug,_this.nome,_this.descrizione,_this.tipo,_this.crediti,const DeepCollectionEquality().hash(_this.limiti),_this.livello);
}

@override
String toString() {
  final _this = this as PianoStore;
  return 'PianoStore(slug: ${_this.slug}, nome: ${_this.nome}, descrizione: ${_this.descrizione}, tipo: ${_this.tipo}, crediti: ${_this.crediti}, limiti: ${_this.limiti}, livello: ${_this.livello})';
}


}

/// @nodoc
abstract mixin class $PianoStoreCopyWith<$Res>  {
  factory $PianoStoreCopyWith(PianoStore value, $Res Function(PianoStore) _then) = _$PianoStoreCopyWithImpl;
@useResult
$Res call({
 String slug, String nome, String? descrizione, String tipo, int crediti, Map<String, num> limiti, int livello
});




}
/// @nodoc
class _$PianoStoreCopyWithImpl<$Res>
    implements $PianoStoreCopyWith<$Res> {
  _$PianoStoreCopyWithImpl(this._self, this._then);

  final PianoStore _self;
  final $Res Function(PianoStore) _then;

/// Create a copy of PianoStore
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? slug = null,Object? nome = null,Object? descrizione = freezed,Object? tipo = null,Object? crediti = null,Object? limiti = null,Object? livello = null,}) {
  return _then(PianoStore(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,crediti: null == crediti ? _self.crediti : crediti // ignore: cast_nullable_to_non_nullable
as int,limiti: null == limiti ? _self.limiti : limiti // ignore: cast_nullable_to_non_nullable
as Map<String, num>,livello: null == livello ? _self.livello : livello // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [PianoStore].
extension PianoStorePatterns on PianoStore {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PianoStore value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PianoStore() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PianoStore value)  $default,){
final _that = this;
switch (_that) {
case _PianoStore():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PianoStore value)?  $default,){
final _that = this;
switch (_that) {
case _PianoStore() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String slug,  String nome,  String? descrizione,  String tipo,  int crediti,  Map<String, num> limiti,  int livello)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PianoStore() when $default != null:
return $default(_that.slug,_that.nome,_that.descrizione,_that.tipo,_that.crediti,_that.limiti,_that.livello);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String slug,  String nome,  String? descrizione,  String tipo,  int crediti,  Map<String, num> limiti,  int livello)  $default,) {final _that = this;
switch (_that) {
case _PianoStore():
return $default(_that.slug,_that.nome,_that.descrizione,_that.tipo,_that.crediti,_that.limiti,_that.livello);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String slug,  String nome,  String? descrizione,  String tipo,  int crediti,  Map<String, num> limiti,  int livello)?  $default,) {final _that = this;
switch (_that) {
case _PianoStore() when $default != null:
return $default(_that.slug,_that.nome,_that.descrizione,_that.tipo,_that.crediti,_that.limiti,_that.livello);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PianoStore implements PianoStore {
  const _PianoStore({required this.slug, required this.nome, this.descrizione, required this.tipo, this.crediti = 0,  Map<String, num> limiti = const <String, num>{}, this.livello = 0}): _limiti = limiti;
  factory _PianoStore.fromJson(Map<String, dynamic> json) => _$PianoStoreFromJson(json);

@override final  String slug;
@override final  String nome;
@override final  String? descrizione;
/// `pacchetto` o `abbonamento`.
@override final  String tipo;
@override@JsonKey() final  int crediti;
 final  Map<String, num> _limiti;
@override@JsonKey() Map<String, num> get limiti {
  if (_limiti is EqualUnmodifiableMapView) return _limiti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_limiti);
}

@override@JsonKey() final  int livello;

/// Create a copy of PianoStore
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PianoStoreCopyWith<_PianoStore> get copyWith => __$PianoStoreCopyWithImpl<_PianoStore>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PianoStoreToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PianoStore&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.descrizione, descrizione) || other.descrizione == descrizione)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.crediti, crediti) || other.crediti == crediti)&&const DeepCollectionEquality().equals(other.limiti, _limiti)&&(identical(other.livello, livello) || other.livello == livello));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,slug,nome,descrizione,tipo,crediti,const DeepCollectionEquality().hash(_limiti),livello);
}

@override
String toString() {
    return 'PianoStore(slug: $slug, nome: $nome, descrizione: $descrizione, tipo: $tipo, crediti: $crediti, limiti: $limiti, livello: $livello)';
}


}

/// @nodoc
abstract mixin class _$PianoStoreCopyWith<$Res> implements $PianoStoreCopyWith<$Res> {
  factory _$PianoStoreCopyWith(_PianoStore value, $Res Function(_PianoStore) _then) = __$PianoStoreCopyWithImpl;
@override @useResult
$Res call({
 String slug, String nome, String? descrizione, String tipo, int crediti, Map<String, num> limiti, int livello
});




}
/// @nodoc
class __$PianoStoreCopyWithImpl<$Res>
    implements _$PianoStoreCopyWith<$Res> {
  __$PianoStoreCopyWithImpl(this._self, this._then);

  final _PianoStore _self;
  final $Res Function(_PianoStore) _then;

/// Create a copy of PianoStore
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? slug = null,Object? nome = null,Object? descrizione = freezed,Object? tipo = null,Object? crediti = null,Object? limiti = null,Object? livello = null,}) {
  return _then(_PianoStore(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,crediti: null == crediti ? _self.crediti : crediti // ignore: cast_nullable_to_non_nullable
as int,limiti: null == limiti ? _self._limiti : limiti // ignore: cast_nullable_to_non_nullable
as Map<String, num>,livello: null == livello ? _self.livello : livello // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$ProdottoStore {

/// L'ID del prodotto nello store (per Google l'abbonamento, senza il base plan).
 String get productId;/// Google: il base plan dell'abbonamento (`mensile`, `annuale`, `prova`); Apple: sempre nullo.
 String? get basePlan;/// `consumabile` (un pacchetto di crediti) o `abbonamento`.
 String get tipo; bool get annuale;/// L'annuale della prova: metà prezzo, con la prova gratuita dello store.
 bool get prova; PianoStore get piano;
/// Create a copy of ProdottoStore
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProdottoStoreCopyWith<ProdottoStore> get copyWith => _$ProdottoStoreCopyWithImpl<ProdottoStore>(this as ProdottoStore, _$identity);

  /// Serializes this ProdottoStore to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ProdottoStore;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProdottoStore&&(identical(other.productId, _this.productId) || other.productId == _this.productId)&&(identical(other.basePlan, _this.basePlan) || other.basePlan == _this.basePlan)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.annuale, _this.annuale) || other.annuale == _this.annuale)&&(identical(other.prova, _this.prova) || other.prova == _this.prova)&&(identical(other.piano, _this.piano) || other.piano == _this.piano));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ProdottoStore;
  return Object.hash(runtimeType,_this.productId,_this.basePlan,_this.tipo,_this.annuale,_this.prova,_this.piano);
}

@override
String toString() {
  final _this = this as ProdottoStore;
  return 'ProdottoStore(productId: ${_this.productId}, basePlan: ${_this.basePlan}, tipo: ${_this.tipo}, annuale: ${_this.annuale}, prova: ${_this.prova}, piano: ${_this.piano})';
}


}

/// @nodoc
abstract mixin class $ProdottoStoreCopyWith<$Res>  {
  factory $ProdottoStoreCopyWith(ProdottoStore value, $Res Function(ProdottoStore) _then) = _$ProdottoStoreCopyWithImpl;
@useResult
$Res call({
 String productId, String? basePlan, String tipo, bool annuale, bool prova, PianoStore piano
});


$PianoStoreCopyWith<$Res> get piano;

}
/// @nodoc
class _$ProdottoStoreCopyWithImpl<$Res>
    implements $ProdottoStoreCopyWith<$Res> {
  _$ProdottoStoreCopyWithImpl(this._self, this._then);

  final ProdottoStore _self;
  final $Res Function(ProdottoStore) _then;

/// Create a copy of ProdottoStore
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? productId = null,Object? basePlan = freezed,Object? tipo = null,Object? annuale = null,Object? prova = null,Object? piano = null,}) {
  return _then(ProdottoStore(
productId: null == productId ? _self.productId : productId // ignore: cast_nullable_to_non_nullable
as String,basePlan: freezed == basePlan ? _self.basePlan : basePlan // ignore: cast_nullable_to_non_nullable
as String?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,prova: null == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as bool,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as PianoStore,
  ));
}
/// Create a copy of ProdottoStore
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PianoStoreCopyWith<$Res> get piano {
  
  return $PianoStoreCopyWith<$Res>(_self.piano, (value) {
    return _then(_self.copyWith(piano: value));
  });
}
}


/// Adds pattern-matching-related methods to [ProdottoStore].
extension ProdottoStorePatterns on ProdottoStore {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ProdottoStore value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ProdottoStore() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ProdottoStore value)  $default,){
final _that = this;
switch (_that) {
case _ProdottoStore():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ProdottoStore value)?  $default,){
final _that = this;
switch (_that) {
case _ProdottoStore() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String productId,  String? basePlan,  String tipo,  bool annuale,  bool prova,  PianoStore piano)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ProdottoStore() when $default != null:
return $default(_that.productId,_that.basePlan,_that.tipo,_that.annuale,_that.prova,_that.piano);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String productId,  String? basePlan,  String tipo,  bool annuale,  bool prova,  PianoStore piano)  $default,) {final _that = this;
switch (_that) {
case _ProdottoStore():
return $default(_that.productId,_that.basePlan,_that.tipo,_that.annuale,_that.prova,_that.piano);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String productId,  String? basePlan,  String tipo,  bool annuale,  bool prova,  PianoStore piano)?  $default,) {final _that = this;
switch (_that) {
case _ProdottoStore() when $default != null:
return $default(_that.productId,_that.basePlan,_that.tipo,_that.annuale,_that.prova,_that.piano);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ProdottoStore implements ProdottoStore {
  const _ProdottoStore({required this.productId, this.basePlan, required this.tipo, this.annuale = false, this.prova = false, required this.piano});
  factory _ProdottoStore.fromJson(Map<String, dynamic> json) => _$ProdottoStoreFromJson(json);

/// L'ID del prodotto nello store (per Google l'abbonamento, senza il base plan).
@override final  String productId;
/// Google: il base plan dell'abbonamento (`mensile`, `annuale`, `prova`); Apple: sempre nullo.
@override final  String? basePlan;
/// `consumabile` (un pacchetto di crediti) o `abbonamento`.
@override final  String tipo;
@override@JsonKey() final  bool annuale;
/// L'annuale della prova: metà prezzo, con la prova gratuita dello store.
@override@JsonKey() final  bool prova;
@override final  PianoStore piano;

/// Create a copy of ProdottoStore
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProdottoStoreCopyWith<_ProdottoStore> get copyWith => __$ProdottoStoreCopyWithImpl<_ProdottoStore>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProdottoStoreToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProdottoStore&&(identical(other.productId, productId) || other.productId == productId)&&(identical(other.basePlan, basePlan) || other.basePlan == basePlan)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.annuale, annuale) || other.annuale == annuale)&&(identical(other.prova, prova) || other.prova == prova)&&(identical(other.piano, piano) || other.piano == piano));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,productId,basePlan,tipo,annuale,prova,piano);
}

@override
String toString() {
    return 'ProdottoStore(productId: $productId, basePlan: $basePlan, tipo: $tipo, annuale: $annuale, prova: $prova, piano: $piano)';
}


}

/// @nodoc
abstract mixin class _$ProdottoStoreCopyWith<$Res> implements $ProdottoStoreCopyWith<$Res> {
  factory _$ProdottoStoreCopyWith(_ProdottoStore value, $Res Function(_ProdottoStore) _then) = __$ProdottoStoreCopyWithImpl;
@override @useResult
$Res call({
 String productId, String? basePlan, String tipo, bool annuale, bool prova, PianoStore piano
});


@override $PianoStoreCopyWith<$Res> get piano;

}
/// @nodoc
class __$ProdottoStoreCopyWithImpl<$Res>
    implements _$ProdottoStoreCopyWith<$Res> {
  __$ProdottoStoreCopyWithImpl(this._self, this._then);

  final _ProdottoStore _self;
  final $Res Function(_ProdottoStore) _then;

/// Create a copy of ProdottoStore
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? productId = null,Object? basePlan = freezed,Object? tipo = null,Object? annuale = null,Object? prova = null,Object? piano = null,}) {
  return _then(_ProdottoStore(
productId: null == productId ? _self.productId : productId // ignore: cast_nullable_to_non_nullable
as String,basePlan: freezed == basePlan ? _self.basePlan : basePlan // ignore: cast_nullable_to_non_nullable
as String?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,prova: null == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as bool,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as PianoStore,
  ));
}

/// Create a copy of ProdottoStore
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PianoStoreCopyWith<$Res> get piano {
  
  return $PianoStoreCopyWith<$Res>(_self.piano, (value) {
    return _then(_self.copyWith(piano: value));
  });
}
}


/// @nodoc
mixin _$PulsanteStripe {

 String get modalita; String? get avviso; bool get mostra;
/// Create a copy of PulsanteStripe
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PulsanteStripeCopyWith<PulsanteStripe> get copyWith => _$PulsanteStripeCopyWithImpl<PulsanteStripe>(this as PulsanteStripe, _$identity);

  /// Serializes this PulsanteStripe to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PulsanteStripe;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PulsanteStripe&&(identical(other.modalita, _this.modalita) || other.modalita == _this.modalita)&&(identical(other.avviso, _this.avviso) || other.avviso == _this.avviso)&&(identical(other.mostra, _this.mostra) || other.mostra == _this.mostra));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PulsanteStripe;
  return Object.hash(runtimeType,_this.modalita,_this.avviso,_this.mostra);
}

@override
String toString() {
  final _this = this as PulsanteStripe;
  return 'PulsanteStripe(modalita: ${_this.modalita}, avviso: ${_this.avviso}, mostra: ${_this.mostra})';
}


}

/// @nodoc
abstract mixin class $PulsanteStripeCopyWith<$Res>  {
  factory $PulsanteStripeCopyWith(PulsanteStripe value, $Res Function(PulsanteStripe) _then) = _$PulsanteStripeCopyWithImpl;
@useResult
$Res call({
 String modalita, String? avviso, bool mostra
});




}
/// @nodoc
class _$PulsanteStripeCopyWithImpl<$Res>
    implements $PulsanteStripeCopyWith<$Res> {
  _$PulsanteStripeCopyWithImpl(this._self, this._then);

  final PulsanteStripe _self;
  final $Res Function(PulsanteStripe) _then;

/// Create a copy of PulsanteStripe
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? modalita = null,Object? avviso = freezed,Object? mostra = null,}) {
  return _then(PulsanteStripe(
modalita: null == modalita ? _self.modalita : modalita // ignore: cast_nullable_to_non_nullable
as String,avviso: freezed == avviso ? _self.avviso : avviso // ignore: cast_nullable_to_non_nullable
as String?,mostra: null == mostra ? _self.mostra : mostra // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [PulsanteStripe].
extension PulsanteStripePatterns on PulsanteStripe {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PulsanteStripe value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PulsanteStripe() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PulsanteStripe value)  $default,){
final _that = this;
switch (_that) {
case _PulsanteStripe():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PulsanteStripe value)?  $default,){
final _that = this;
switch (_that) {
case _PulsanteStripe() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String modalita,  String? avviso,  bool mostra)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PulsanteStripe() when $default != null:
return $default(_that.modalita,_that.avviso,_that.mostra);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String modalita,  String? avviso,  bool mostra)  $default,) {final _that = this;
switch (_that) {
case _PulsanteStripe():
return $default(_that.modalita,_that.avviso,_that.mostra);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String modalita,  String? avviso,  bool mostra)?  $default,) {final _that = this;
switch (_that) {
case _PulsanteStripe() when $default != null:
return $default(_that.modalita,_that.avviso,_that.mostra);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PulsanteStripe implements PulsanteStripe {
  const _PulsanteStripe({this.modalita = 'nascosto', this.avviso, this.mostra = false});
  factory _PulsanteStripe.fromJson(Map<String, dynamic> json) => _$PulsanteStripeFromJson(json);

@override@JsonKey() final  String modalita;
@override final  String? avviso;
@override@JsonKey() final  bool mostra;

/// Create a copy of PulsanteStripe
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PulsanteStripeCopyWith<_PulsanteStripe> get copyWith => __$PulsanteStripeCopyWithImpl<_PulsanteStripe>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PulsanteStripeToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PulsanteStripe&&(identical(other.modalita, modalita) || other.modalita == modalita)&&(identical(other.avviso, avviso) || other.avviso == avviso)&&(identical(other.mostra, mostra) || other.mostra == mostra));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,modalita,avviso,mostra);
}

@override
String toString() {
    return 'PulsanteStripe(modalita: $modalita, avviso: $avviso, mostra: $mostra)';
}


}

/// @nodoc
abstract mixin class _$PulsanteStripeCopyWith<$Res> implements $PulsanteStripeCopyWith<$Res> {
  factory _$PulsanteStripeCopyWith(_PulsanteStripe value, $Res Function(_PulsanteStripe) _then) = __$PulsanteStripeCopyWithImpl;
@override @useResult
$Res call({
 String modalita, String? avviso, bool mostra
});




}
/// @nodoc
class __$PulsanteStripeCopyWithImpl<$Res>
    implements _$PulsanteStripeCopyWith<$Res> {
  __$PulsanteStripeCopyWithImpl(this._self, this._then);

  final _PulsanteStripe _self;
  final $Res Function(_PulsanteStripe) _then;

/// Create a copy of PulsanteStripe
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? modalita = null,Object? avviso = freezed,Object? mostra = null,}) {
  return _then(_PulsanteStripe(
modalita: null == modalita ? _self.modalita : modalita // ignore: cast_nullable_to_non_nullable
as String,avviso: freezed == avviso ? _self.avviso : avviso // ignore: cast_nullable_to_non_nullable
as String?,mostra: null == mostra ? _self.mostra : mostra // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$CatalogoStore {

 String get piattaforma; String? get paese; List<ProdottoStore> get prodotti; PulsanteStripe get stripe; String? get appAccountToken;
/// Create a copy of CatalogoStore
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CatalogoStoreCopyWith<CatalogoStore> get copyWith => _$CatalogoStoreCopyWithImpl<CatalogoStore>(this as CatalogoStore, _$identity);

  /// Serializes this CatalogoStore to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CatalogoStore;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CatalogoStore&&(identical(other.piattaforma, _this.piattaforma) || other.piattaforma == _this.piattaforma)&&(identical(other.paese, _this.paese) || other.paese == _this.paese)&&const DeepCollectionEquality().equals(other.prodotti, _this.prodotti)&&(identical(other.stripe, _this.stripe) || other.stripe == _this.stripe)&&(identical(other.appAccountToken, _this.appAccountToken) || other.appAccountToken == _this.appAccountToken));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CatalogoStore;
  return Object.hash(runtimeType,_this.piattaforma,_this.paese,const DeepCollectionEquality().hash(_this.prodotti),_this.stripe,_this.appAccountToken);
}

@override
String toString() {
  final _this = this as CatalogoStore;
  return 'CatalogoStore(piattaforma: ${_this.piattaforma}, paese: ${_this.paese}, prodotti: ${_this.prodotti}, stripe: ${_this.stripe}, appAccountToken: ${_this.appAccountToken})';
}


}

/// @nodoc
abstract mixin class $CatalogoStoreCopyWith<$Res>  {
  factory $CatalogoStoreCopyWith(CatalogoStore value, $Res Function(CatalogoStore) _then) = _$CatalogoStoreCopyWithImpl;
@useResult
$Res call({
 String piattaforma, String? paese, List<ProdottoStore> prodotti, PulsanteStripe stripe, String? appAccountToken
});


$PulsanteStripeCopyWith<$Res> get stripe;

}
/// @nodoc
class _$CatalogoStoreCopyWithImpl<$Res>
    implements $CatalogoStoreCopyWith<$Res> {
  _$CatalogoStoreCopyWithImpl(this._self, this._then);

  final CatalogoStore _self;
  final $Res Function(CatalogoStore) _then;

/// Create a copy of CatalogoStore
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? piattaforma = null,Object? paese = freezed,Object? prodotti = null,Object? stripe = null,Object? appAccountToken = freezed,}) {
  return _then(CatalogoStore(
piattaforma: null == piattaforma ? _self.piattaforma : piattaforma // ignore: cast_nullable_to_non_nullable
as String,paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,prodotti: null == prodotti ? _self.prodotti : prodotti // ignore: cast_nullable_to_non_nullable
as List<ProdottoStore>,stripe: null == stripe ? _self.stripe : stripe // ignore: cast_nullable_to_non_nullable
as PulsanteStripe,appAccountToken: freezed == appAccountToken ? _self.appAccountToken : appAccountToken // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of CatalogoStore
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PulsanteStripeCopyWith<$Res> get stripe {
  
  return $PulsanteStripeCopyWith<$Res>(_self.stripe, (value) {
    return _then(_self.copyWith(stripe: value));
  });
}
}


/// Adds pattern-matching-related methods to [CatalogoStore].
extension CatalogoStorePatterns on CatalogoStore {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CatalogoStore value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CatalogoStore() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CatalogoStore value)  $default,){
final _that = this;
switch (_that) {
case _CatalogoStore():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CatalogoStore value)?  $default,){
final _that = this;
switch (_that) {
case _CatalogoStore() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String piattaforma,  String? paese,  List<ProdottoStore> prodotti,  PulsanteStripe stripe,  String? appAccountToken)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CatalogoStore() when $default != null:
return $default(_that.piattaforma,_that.paese,_that.prodotti,_that.stripe,_that.appAccountToken);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String piattaforma,  String? paese,  List<ProdottoStore> prodotti,  PulsanteStripe stripe,  String? appAccountToken)  $default,) {final _that = this;
switch (_that) {
case _CatalogoStore():
return $default(_that.piattaforma,_that.paese,_that.prodotti,_that.stripe,_that.appAccountToken);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String piattaforma,  String? paese,  List<ProdottoStore> prodotti,  PulsanteStripe stripe,  String? appAccountToken)?  $default,) {final _that = this;
switch (_that) {
case _CatalogoStore() when $default != null:
return $default(_that.piattaforma,_that.paese,_that.prodotti,_that.stripe,_that.appAccountToken);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CatalogoStore implements CatalogoStore {
  const _CatalogoStore({required this.piattaforma, this.paese,  List<ProdottoStore> prodotti = const <ProdottoStore>[], this.stripe = const PulsanteStripe(), this.appAccountToken}): _prodotti = prodotti;
  factory _CatalogoStore.fromJson(Map<String, dynamic> json) => _$CatalogoStoreFromJson(json);

@override final  String piattaforma;
@override final  String? paese;
 final  List<ProdottoStore> _prodotti;
@override@JsonKey() List<ProdottoStore> get prodotti {
  if (_prodotti is EqualUnmodifiableListView) return _prodotti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_prodotti);
}

@override@JsonKey() final  PulsanteStripe stripe;
@override final  String? appAccountToken;

/// Create a copy of CatalogoStore
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CatalogoStoreCopyWith<_CatalogoStore> get copyWith => __$CatalogoStoreCopyWithImpl<_CatalogoStore>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CatalogoStoreToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CatalogoStore&&(identical(other.piattaforma, piattaforma) || other.piattaforma == piattaforma)&&(identical(other.paese, paese) || other.paese == paese)&&const DeepCollectionEquality().equals(other.prodotti, _prodotti)&&(identical(other.stripe, stripe) || other.stripe == stripe)&&(identical(other.appAccountToken, appAccountToken) || other.appAccountToken == appAccountToken));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,piattaforma,paese,const DeepCollectionEquality().hash(_prodotti),stripe,appAccountToken);
}

@override
String toString() {
    return 'CatalogoStore(piattaforma: $piattaforma, paese: $paese, prodotti: $prodotti, stripe: $stripe, appAccountToken: $appAccountToken)';
}


}

/// @nodoc
abstract mixin class _$CatalogoStoreCopyWith<$Res> implements $CatalogoStoreCopyWith<$Res> {
  factory _$CatalogoStoreCopyWith(_CatalogoStore value, $Res Function(_CatalogoStore) _then) = __$CatalogoStoreCopyWithImpl;
@override @useResult
$Res call({
 String piattaforma, String? paese, List<ProdottoStore> prodotti, PulsanteStripe stripe, String? appAccountToken
});


@override $PulsanteStripeCopyWith<$Res> get stripe;

}
/// @nodoc
class __$CatalogoStoreCopyWithImpl<$Res>
    implements _$CatalogoStoreCopyWith<$Res> {
  __$CatalogoStoreCopyWithImpl(this._self, this._then);

  final _CatalogoStore _self;
  final $Res Function(_CatalogoStore) _then;

/// Create a copy of CatalogoStore
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? piattaforma = null,Object? paese = freezed,Object? prodotti = null,Object? stripe = null,Object? appAccountToken = freezed,}) {
  return _then(_CatalogoStore(
piattaforma: null == piattaforma ? _self.piattaforma : piattaforma // ignore: cast_nullable_to_non_nullable
as String,paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,prodotti: null == prodotti ? _self._prodotti : prodotti // ignore: cast_nullable_to_non_nullable
as List<ProdottoStore>,stripe: null == stripe ? _self.stripe : stripe // ignore: cast_nullable_to_non_nullable
as PulsanteStripe,appAccountToken: freezed == appAccountToken ? _self.appAccountToken : appAccountToken // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of CatalogoStore
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PulsanteStripeCopyWith<$Res> get stripe {
  
  return $PulsanteStripeCopyWith<$Res>(_self.stripe, (value) {
    return _then(_self.copyWith(stripe: value));
  });
}
}


/// @nodoc
mixin _$AcquistoRegistrato {

 String get productId; String get tipo;/// `in_attesa`, `accreditato`, `rimborsato`, `revocato`, `scaduto`.
 String get stato;/// Già confermato allo store dal server (Google: consumato o riconosciuto).
 bool get confermato; String get ambiente;
/// Create a copy of AcquistoRegistrato
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AcquistoRegistratoCopyWith<AcquistoRegistrato> get copyWith => _$AcquistoRegistratoCopyWithImpl<AcquistoRegistrato>(this as AcquistoRegistrato, _$identity);

  /// Serializes this AcquistoRegistrato to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as AcquistoRegistrato;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AcquistoRegistrato&&(identical(other.productId, _this.productId) || other.productId == _this.productId)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.stato, _this.stato) || other.stato == _this.stato)&&(identical(other.confermato, _this.confermato) || other.confermato == _this.confermato)&&(identical(other.ambiente, _this.ambiente) || other.ambiente == _this.ambiente));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as AcquistoRegistrato;
  return Object.hash(runtimeType,_this.productId,_this.tipo,_this.stato,_this.confermato,_this.ambiente);
}

@override
String toString() {
  final _this = this as AcquistoRegistrato;
  return 'AcquistoRegistrato(productId: ${_this.productId}, tipo: ${_this.tipo}, stato: ${_this.stato}, confermato: ${_this.confermato}, ambiente: ${_this.ambiente})';
}


}

/// @nodoc
abstract mixin class $AcquistoRegistratoCopyWith<$Res>  {
  factory $AcquistoRegistratoCopyWith(AcquistoRegistrato value, $Res Function(AcquistoRegistrato) _then) = _$AcquistoRegistratoCopyWithImpl;
@useResult
$Res call({
 String productId, String tipo, String stato, bool confermato, String ambiente
});




}
/// @nodoc
class _$AcquistoRegistratoCopyWithImpl<$Res>
    implements $AcquistoRegistratoCopyWith<$Res> {
  _$AcquistoRegistratoCopyWithImpl(this._self, this._then);

  final AcquistoRegistrato _self;
  final $Res Function(AcquistoRegistrato) _then;

/// Create a copy of AcquistoRegistrato
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? productId = null,Object? tipo = null,Object? stato = null,Object? confermato = null,Object? ambiente = null,}) {
  return _then(AcquistoRegistrato(
productId: null == productId ? _self.productId : productId // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,stato: null == stato ? _self.stato : stato // ignore: cast_nullable_to_non_nullable
as String,confermato: null == confermato ? _self.confermato : confermato // ignore: cast_nullable_to_non_nullable
as bool,ambiente: null == ambiente ? _self.ambiente : ambiente // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [AcquistoRegistrato].
extension AcquistoRegistratoPatterns on AcquistoRegistrato {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AcquistoRegistrato value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AcquistoRegistrato() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AcquistoRegistrato value)  $default,){
final _that = this;
switch (_that) {
case _AcquistoRegistrato():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AcquistoRegistrato value)?  $default,){
final _that = this;
switch (_that) {
case _AcquistoRegistrato() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String productId,  String tipo,  String stato,  bool confermato,  String ambiente)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AcquistoRegistrato() when $default != null:
return $default(_that.productId,_that.tipo,_that.stato,_that.confermato,_that.ambiente);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String productId,  String tipo,  String stato,  bool confermato,  String ambiente)  $default,) {final _that = this;
switch (_that) {
case _AcquistoRegistrato():
return $default(_that.productId,_that.tipo,_that.stato,_that.confermato,_that.ambiente);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String productId,  String tipo,  String stato,  bool confermato,  String ambiente)?  $default,) {final _that = this;
switch (_that) {
case _AcquistoRegistrato() when $default != null:
return $default(_that.productId,_that.tipo,_that.stato,_that.confermato,_that.ambiente);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AcquistoRegistrato implements AcquistoRegistrato {
  const _AcquistoRegistrato({required this.productId, required this.tipo, required this.stato, this.confermato = false, this.ambiente = 'production'});
  factory _AcquistoRegistrato.fromJson(Map<String, dynamic> json) => _$AcquistoRegistratoFromJson(json);

@override final  String productId;
@override final  String tipo;
/// `in_attesa`, `accreditato`, `rimborsato`, `revocato`, `scaduto`.
@override final  String stato;
/// Già confermato allo store dal server (Google: consumato o riconosciuto).
@override@JsonKey() final  bool confermato;
@override@JsonKey() final  String ambiente;

/// Create a copy of AcquistoRegistrato
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AcquistoRegistratoCopyWith<_AcquistoRegistrato> get copyWith => __$AcquistoRegistratoCopyWithImpl<_AcquistoRegistrato>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AcquistoRegistratoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _AcquistoRegistrato&&(identical(other.productId, productId) || other.productId == productId)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.stato, stato) || other.stato == stato)&&(identical(other.confermato, confermato) || other.confermato == confermato)&&(identical(other.ambiente, ambiente) || other.ambiente == ambiente));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,productId,tipo,stato,confermato,ambiente);
}

@override
String toString() {
    return 'AcquistoRegistrato(productId: $productId, tipo: $tipo, stato: $stato, confermato: $confermato, ambiente: $ambiente)';
}


}

/// @nodoc
abstract mixin class _$AcquistoRegistratoCopyWith<$Res> implements $AcquistoRegistratoCopyWith<$Res> {
  factory _$AcquistoRegistratoCopyWith(_AcquistoRegistrato value, $Res Function(_AcquistoRegistrato) _then) = __$AcquistoRegistratoCopyWithImpl;
@override @useResult
$Res call({
 String productId, String tipo, String stato, bool confermato, String ambiente
});




}
/// @nodoc
class __$AcquistoRegistratoCopyWithImpl<$Res>
    implements _$AcquistoRegistratoCopyWith<$Res> {
  __$AcquistoRegistratoCopyWithImpl(this._self, this._then);

  final _AcquistoRegistrato _self;
  final $Res Function(_AcquistoRegistrato) _then;

/// Create a copy of AcquistoRegistrato
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? productId = null,Object? tipo = null,Object? stato = null,Object? confermato = null,Object? ambiente = null,}) {
  return _then(_AcquistoRegistrato(
productId: null == productId ? _self.productId : productId // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,stato: null == stato ? _self.stato : stato // ignore: cast_nullable_to_non_nullable
as String,confermato: null == confermato ? _self.confermato : confermato // ignore: cast_nullable_to_non_nullable
as bool,ambiente: null == ambiente ? _self.ambiente : ambiente // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$EsitoVerificaStore {

 String get esito; AcquistoRegistrato get acquisto; int get saldo; AbbonamentoDettaglio? get abbonamento;
/// Create a copy of EsitoVerificaStore
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EsitoVerificaStoreCopyWith<EsitoVerificaStore> get copyWith => _$EsitoVerificaStoreCopyWithImpl<EsitoVerificaStore>(this as EsitoVerificaStore, _$identity);

  /// Serializes this EsitoVerificaStore to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as EsitoVerificaStore;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EsitoVerificaStore&&(identical(other.esito, _this.esito) || other.esito == _this.esito)&&(identical(other.acquisto, _this.acquisto) || other.acquisto == _this.acquisto)&&(identical(other.saldo, _this.saldo) || other.saldo == _this.saldo)&&(identical(other.abbonamento, _this.abbonamento) || other.abbonamento == _this.abbonamento));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as EsitoVerificaStore;
  return Object.hash(runtimeType,_this.esito,_this.acquisto,_this.saldo,_this.abbonamento);
}

@override
String toString() {
  final _this = this as EsitoVerificaStore;
  return 'EsitoVerificaStore(esito: ${_this.esito}, acquisto: ${_this.acquisto}, saldo: ${_this.saldo}, abbonamento: ${_this.abbonamento})';
}


}

/// @nodoc
abstract mixin class $EsitoVerificaStoreCopyWith<$Res>  {
  factory $EsitoVerificaStoreCopyWith(EsitoVerificaStore value, $Res Function(EsitoVerificaStore) _then) = _$EsitoVerificaStoreCopyWithImpl;
@useResult
$Res call({
 String esito, AcquistoRegistrato acquisto, int saldo, AbbonamentoDettaglio? abbonamento
});


$AcquistoRegistratoCopyWith<$Res> get acquisto;$AbbonamentoDettaglioCopyWith<$Res>? get abbonamento;

}
/// @nodoc
class _$EsitoVerificaStoreCopyWithImpl<$Res>
    implements $EsitoVerificaStoreCopyWith<$Res> {
  _$EsitoVerificaStoreCopyWithImpl(this._self, this._then);

  final EsitoVerificaStore _self;
  final $Res Function(EsitoVerificaStore) _then;

/// Create a copy of EsitoVerificaStore
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? esito = null,Object? acquisto = null,Object? saldo = null,Object? abbonamento = freezed,}) {
  return _then(EsitoVerificaStore(
esito: null == esito ? _self.esito : esito // ignore: cast_nullable_to_non_nullable
as String,acquisto: null == acquisto ? _self.acquisto : acquisto // ignore: cast_nullable_to_non_nullable
as AcquistoRegistrato,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,abbonamento: freezed == abbonamento ? _self.abbonamento : abbonamento // ignore: cast_nullable_to_non_nullable
as AbbonamentoDettaglio?,
  ));
}
/// Create a copy of EsitoVerificaStore
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AcquistoRegistratoCopyWith<$Res> get acquisto {
  
  return $AcquistoRegistratoCopyWith<$Res>(_self.acquisto, (value) {
    return _then(_self.copyWith(acquisto: value));
  });
}/// Create a copy of EsitoVerificaStore
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AbbonamentoDettaglioCopyWith<$Res>? get abbonamento {
    if (_self.abbonamento == null) {
    return null;
  }

  return $AbbonamentoDettaglioCopyWith<$Res>(_self.abbonamento!, (value) {
    return _then(_self.copyWith(abbonamento: value));
  });
}
}


/// Adds pattern-matching-related methods to [EsitoVerificaStore].
extension EsitoVerificaStorePatterns on EsitoVerificaStore {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EsitoVerificaStore value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EsitoVerificaStore() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EsitoVerificaStore value)  $default,){
final _that = this;
switch (_that) {
case _EsitoVerificaStore():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EsitoVerificaStore value)?  $default,){
final _that = this;
switch (_that) {
case _EsitoVerificaStore() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String esito,  AcquistoRegistrato acquisto,  int saldo,  AbbonamentoDettaglio? abbonamento)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EsitoVerificaStore() when $default != null:
return $default(_that.esito,_that.acquisto,_that.saldo,_that.abbonamento);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String esito,  AcquistoRegistrato acquisto,  int saldo,  AbbonamentoDettaglio? abbonamento)  $default,) {final _that = this;
switch (_that) {
case _EsitoVerificaStore():
return $default(_that.esito,_that.acquisto,_that.saldo,_that.abbonamento);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String esito,  AcquistoRegistrato acquisto,  int saldo,  AbbonamentoDettaglio? abbonamento)?  $default,) {final _that = this;
switch (_that) {
case _EsitoVerificaStore() when $default != null:
return $default(_that.esito,_that.acquisto,_that.saldo,_that.abbonamento);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EsitoVerificaStore implements EsitoVerificaStore {
  const _EsitoVerificaStore({this.esito = '', required this.acquisto, this.saldo = 0, this.abbonamento});
  factory _EsitoVerificaStore.fromJson(Map<String, dynamic> json) => _$EsitoVerificaStoreFromJson(json);

@override@JsonKey() final  String esito;
@override final  AcquistoRegistrato acquisto;
@override@JsonKey() final  int saldo;
@override final  AbbonamentoDettaglio? abbonamento;

/// Create a copy of EsitoVerificaStore
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EsitoVerificaStoreCopyWith<_EsitoVerificaStore> get copyWith => __$EsitoVerificaStoreCopyWithImpl<_EsitoVerificaStore>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EsitoVerificaStoreToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _EsitoVerificaStore&&(identical(other.esito, esito) || other.esito == esito)&&(identical(other.acquisto, acquisto) || other.acquisto == acquisto)&&(identical(other.saldo, saldo) || other.saldo == saldo)&&(identical(other.abbonamento, abbonamento) || other.abbonamento == abbonamento));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,esito,acquisto,saldo,abbonamento);
}

@override
String toString() {
    return 'EsitoVerificaStore(esito: $esito, acquisto: $acquisto, saldo: $saldo, abbonamento: $abbonamento)';
}


}

/// @nodoc
abstract mixin class _$EsitoVerificaStoreCopyWith<$Res> implements $EsitoVerificaStoreCopyWith<$Res> {
  factory _$EsitoVerificaStoreCopyWith(_EsitoVerificaStore value, $Res Function(_EsitoVerificaStore) _then) = __$EsitoVerificaStoreCopyWithImpl;
@override @useResult
$Res call({
 String esito, AcquistoRegistrato acquisto, int saldo, AbbonamentoDettaglio? abbonamento
});


@override $AcquistoRegistratoCopyWith<$Res> get acquisto;@override $AbbonamentoDettaglioCopyWith<$Res>? get abbonamento;

}
/// @nodoc
class __$EsitoVerificaStoreCopyWithImpl<$Res>
    implements _$EsitoVerificaStoreCopyWith<$Res> {
  __$EsitoVerificaStoreCopyWithImpl(this._self, this._then);

  final _EsitoVerificaStore _self;
  final $Res Function(_EsitoVerificaStore) _then;

/// Create a copy of EsitoVerificaStore
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? esito = null,Object? acquisto = null,Object? saldo = null,Object? abbonamento = freezed,}) {
  return _then(_EsitoVerificaStore(
esito: null == esito ? _self.esito : esito // ignore: cast_nullable_to_non_nullable
as String,acquisto: null == acquisto ? _self.acquisto : acquisto // ignore: cast_nullable_to_non_nullable
as AcquistoRegistrato,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,abbonamento: freezed == abbonamento ? _self.abbonamento : abbonamento // ignore: cast_nullable_to_non_nullable
as AbbonamentoDettaglio?,
  ));
}

/// Create a copy of EsitoVerificaStore
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AcquistoRegistratoCopyWith<$Res> get acquisto {
  
  return $AcquistoRegistratoCopyWith<$Res>(_self.acquisto, (value) {
    return _then(_self.copyWith(acquisto: value));
  });
}/// Create a copy of EsitoVerificaStore
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AbbonamentoDettaglioCopyWith<$Res>? get abbonamento {
    if (_self.abbonamento == null) {
    return null;
  }

  return $AbbonamentoDettaglioCopyWith<$Res>(_self.abbonamento!, (value) {
    return _then(_self.copyWith(abbonamento: value));
  });
}
}

// dart format on
